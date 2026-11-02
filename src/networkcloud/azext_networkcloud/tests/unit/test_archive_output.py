# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import gzip
import hashlib
import io
import os
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from azext_networkcloud.operations import custom_properties as output
from azure.cli.core.aaz._base import AAZUndefined
from azure.cli.core.azclierror import InvalidArgumentValueError

HOST = "results.blob.core.windows.net"
URL = f"https://{HOST}/results/output.tar.gz?sig=example"


def make_archive(members):
    data = io.BytesIO()
    with tarfile.open(fileobj=data, mode="w") as archive:
        for member, content in members:
            archive.addfile(member, io.BytesIO(content) if content else None)
    return data.getvalue()


def regular_file(name="result.txt", content=b"result"):
    member = tarfile.TarInfo(name)
    member.size = len(content)
    return member, content


class TestArchiveOutput(unittest.TestCase):
    def setUp(self):
        self.archive = gzip.compress(make_archive([regular_file()]))
        self.digest = hashlib.sha256(self.archive).hexdigest()
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.destination = self.directory.name
        self.opener_patch = mock.patch.object(output.urllib.request, "build_opener")
        self.opener = self.opener_patch.start().return_value
        self.addCleanup(self.opener_patch.stop)
        self.opener.open.return_value = io.BytesIO(self.archive)

    def download(self, **kwargs):
        output._download_and_extract(
            kwargs.pop("url", URL),
            self.destination,
            kwargs.pop("host", HOST),
            kwargs.pop("digest", self.digest),
            **kwargs,
        )

    def test_verified_download_extracts(self):
        self.download()
        self.assertEqual(Path(self.destination, "result.txt").read_bytes(), b"result")
        self.opener.open.assert_called_once()
        self.assertEqual(self.opener.open.call_args.kwargs["timeout"], 60)

    def test_download_without_checksum(self):
        output._download_and_extract(URL, self.destination, HOST)
        self.assertEqual(Path(self.destination, "result.txt").read_bytes(), b"result")

    def test_optional_checksum_does_not_bypass_host_validation(self):
        with self.assertRaises(InvalidArgumentValueError):
            self.download(url="https://evil.example/output.tar.gz", digest=None)
        self.opener.open.assert_not_called()

    def test_untrusted_urls_rejected_before_network_or_auth(self):
        for url in (
            f"http://{HOST}/output.tar.gz",
            "file:///tmp/output.tar.gz",
            "https://other.blob.core.windows.net/output.tar.gz",
            f"https://{HOST}.evil.example/output.tar.gz",
            f"https://user@{HOST}/output.tar.gz",
            f"https://{HOST}:8443/output.tar.gz",
            f"https://{HOST}/output.tar.gz#fragment",
            f"https://{HOST}/output\n.tar.gz",
            f"https://{HOST}\\@evil.example/output.tar.gz",
        ):
            with self.subTest(url=url), mock.patch.object(output, "Profile") as profile:
                with self.assertRaises((ValueError, InvalidArgumentValueError)):
                    self.download(url=url, cli_ctx=mock.sentinel.cli_ctx)
                profile.assert_not_called()
        self.opener.open.assert_not_called()

    def test_invalid_trust_inputs_rejected(self):
        for host, digest in (
            ("", self.digest),
            ("*.blob.core.windows.net", self.digest),
            ("https://" + HOST, self.digest),
            (HOST, ""),
            (HOST, "g" * 64),
            (HOST, AAZUndefined),
        ):
            with self.subTest(host=host, digest=digest):
                with self.assertRaises(InvalidArgumentValueError):
                    self.download(host=host, digest=digest)
        self.opener.open.assert_not_called()

    def test_checksum_mismatch_prevents_decompression(self):
        with mock.patch.object(output.gzip, "GzipFile") as decompress:
            with self.assertRaisesRegex(ValueError, "checksum"):
                self.download(digest="0" * 64)
            decompress.assert_not_called()
        self.assertEqual(os.listdir(self.destination), [])

    def test_uppercase_digest_accepted(self):
        self.download(digest=self.digest.upper())

    def test_authenticated_reference_uses_storage_token(self):
        with mock.patch.object(output, "Profile") as profile:
            profile.return_value.get_raw_token.return_value = (
                ("Bearer", "storage-token", {}),
                "subscription",
                "tenant",
            )
            self.download(cli_ctx=mock.sentinel.cli_ctx)
            profile.assert_called_once_with(cli_ctx=mock.sentinel.cli_ctx)
            profile.return_value.get_raw_token.assert_called_once_with(
                resource="https://storage.azure.com/"
            )
        request = self.opener.open.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer storage-token")
        self.assertEqual(request.get_header("X-ms-version"), "2023-11-03")

    def test_redirects_rejected(self):
        for target in ("https://evil.example/", URL, f"http://{HOST}/"):
            with self.subTest(target=target):
                with self.assertRaisesRegex(ValueError, "redirects"):
                    output._NoRedirect().redirect_request(
                        None, None, 302, "", {}, target
                    )
                with self.assertRaisesRegex(ValueError, "redirects"):
                    output._NoRedirect().redirect_request(
                        req=None, fp=None, code=302, msg="", headers={}, newurl=target
                    )

    def test_compressed_download_limit(self):
        with mock.patch.object(output, "MAX_ARCHIVE_BYTES", len(self.archive) - 1):
            with self.assertRaisesRegex(ValueError, "size limit"):
                self.download()
        self.assertEqual(os.listdir(self.destination), [])

    def test_actual_one_gib_copy_boundary(self):
        self.assertEqual(output.MAX_ARCHIVE_BYTES, 1024 * 1024 * 1024)
        chunk = b"x" * output.COPY_CHUNK_BYTES
        for extra_bytes in (0, 1):
            remaining = output.MAX_ARCHIVE_BYTES + extra_bytes

            def read(size):
                nonlocal remaining
                count = min(size, remaining)
                remaining -= count
                return chunk[:count]

            source = mock.Mock()
            source.read.side_effect = read
            destination = mock.Mock()
            with self.subTest(extra_bytes=extra_bytes):
                if extra_bytes:
                    with self.assertRaisesRegex(ValueError, "size limit"):
                        output._copy_bounded(source, destination)
                else:
                    output._copy_bounded(source, destination)
                self.assertEqual(
                    sum(len(call.args[0]) for call in destination.write.call_args_list),
                    output.MAX_ARCHIVE_BYTES,
                )

    def test_decompressed_stream_limit_including_padding(self):
        raw = make_archive([regular_file()])
        for limit in (len(raw) - 1, len(raw)):
            with self.subTest(limit=limit):
                self.opener.open.return_value = io.BytesIO(self.archive)
                with mock.patch.object(output, "MAX_ARCHIVE_BYTES", limit):
                    if limit < len(raw):
                        with self.assertRaisesRegex(ValueError, "size limit"):
                            self.download()
                        self.assertEqual(os.listdir(self.destination), [])
                    else:
                        self.download()

    def extract(self, members, legacy=False):
        with tarfile.open(
            fileobj=io.BytesIO(make_archive(members)), mode="r:"
        ) as archive:
            if legacy:
                with mock.patch.object(tarfile, "data_filter", None):
                    output.CustomActionProperties.safe_extract(
                        archive, self.destination
                    )
            else:
                output.CustomActionProperties.safe_extract(archive, self.destination)

    def test_member_limit_and_exact_boundary(self):
        with mock.patch.object(output, "MAX_ARCHIVE_MEMBERS", 2):
            with self.assertRaisesRegex(ValueError, "member limit"):
                self.extract([regular_file(str(index)) for index in range(3)])
            self.assertEqual(os.listdir(self.destination), [])
            self.extract([regular_file(str(index)) for index in range(2)])
        self.assertEqual(len(os.listdir(self.destination)), 2)

    def test_actual_ten_thousand_member_boundary(self):
        self.assertEqual(output.MAX_ARCHIVE_MEMBERS, 10000)
        member = tarfile.TarInfo("empty")
        for count in (10000, 10001):
            archive = mock.MagicMock()
            archive.__iter__.return_value = iter([member] * count)
            with self.subTest(count=count):
                if count > output.MAX_ARCHIVE_MEMBERS:
                    with self.assertRaisesRegex(ValueError, "member limit"):
                        output.CustomActionProperties.safe_extract(
                            archive, self.destination
                        )
                    archive.extractall.assert_not_called()
                else:
                    output.CustomActionProperties.safe_extract(
                        archive, self.destination
                    )
                    self.assertEqual(
                        len(archive.extractall.call_args.kwargs["members"]), count
                    )

    def test_payload_size_limit_and_exact_boundary(self):
        with mock.patch.object(output, "MAX_ARCHIVE_BYTES", 6):
            with self.assertRaisesRegex(ValueError, "size limit"):
                self.extract([regular_file(), regular_file("other", b"x")])
            self.assertEqual(os.listdir(self.destination), [])
            self.extract([regular_file()])

    def test_traversal_and_special_entries(self):
        for legacy in (False, True):
            for name in ("../outside", "/outside"):
                with self.subTest(legacy=legacy, name=name):
                    with self.assertRaises(ValueError):
                        self.extract([regular_file(name)], legacy)
            for entry_type in (tarfile.CHRTYPE, tarfile.BLKTYPE, tarfile.FIFOTYPE):
                member = tarfile.TarInfo("device")
                member.type = entry_type
                with self.subTest(legacy=legacy, entry_type=entry_type):
                    with self.assertRaises((ValueError, tarfile.TarError)):
                        self.extract([(member, None)], legacy)
        self.assertEqual(os.listdir(self.destination), [])

    def test_legacy_rejects_symbolic_and_hard_links(self):
        for entry_type in (tarfile.SYMTYPE, tarfile.LNKTYPE):
            member = tarfile.TarInfo("link")
            member.type = entry_type
            member.linkname = "result.txt"
            with self.subTest(entry_type=entry_type):
                with self.assertRaisesRegex(ValueError, "links and special"):
                    self.extract([regular_file(), (member, None)], legacy=True)
        self.assertEqual(os.listdir(self.destination), [])

    def test_data_filter_blocks_escaping_link(self):
        member = tarfile.TarInfo("link")
        member.type = tarfile.SYMTYPE
        member.linkname = "../outside"
        with self.assertRaises(tarfile.TarError):
            self.extract([(member, None)])

    def test_data_filter_permits_safe_link(self):
        member = tarfile.TarInfo("link")
        member.type = tarfile.SYMTYPE
        member.linkname = "result.txt"
        self.extract([regular_file(), (member, None)])
        self.assertEqual(Path(self.destination, "link").read_bytes(), b"result")

    def test_legacy_resolves_existing_destination_symlinks(self):
        with tempfile.TemporaryDirectory() as outside:
            Path(self.destination, "link").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                self.extract([regular_file("link/escaped")], legacy=True)
            self.assertEqual(os.listdir(outside), [])

    def test_data_filter_is_explicit(self):
        with mock.patch.object(tarfile.TarFile, "extractall") as extract:
            self.extract([regular_file()])
        self.assertEqual(extract.call_args.kwargs["filter"], "data")

    def test_legacy_regular_file(self):
        self.extract([regular_file()], legacy=True)
        self.assertEqual(Path(self.destination, "result.txt").read_bytes(), b"result")
