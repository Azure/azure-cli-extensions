import pydash as _
from azext_arcdata.kubernetes_sdk.arc_docker_image_service import (
    ArcDataImageService,
)
from azext_arcdata.core.util import retry_method


# todo: these are integration tests used for debugging early,  we need to create recordings and wire these up for unit testing.
class TestArcDataImageService(object):
    def test_remote_imagetag_list(self):
        # versions = ArcDataImageService.get_available_image_versions("arc", True)
        # assert versions.index("v1.0.0_2021-07-30") >= 0
        pass

    def test_image_tag_sort(self):
        imageTags = [
            "1.0.1_test",
            "1.0.2_test",
            "1.0.3",
            "1.0.10",
            "some invalid tag",
        ]
        versions = ArcDataImageService.resolve_valid_image_versions(imageTags)
        assert _.matches(["1.0.10", "1.0.3", "1.0.2_test", "1.0.1_test"])(
            versions
        )

    def test_image_tag_validation(self):
        assert ArcDataImageService.validate_image_tag("20210102.4")
        assert ArcDataImageService.validate_image_tag("v1.0.0_label")
        assert ArcDataImageService.validate_image_tag("v1.0.0")
        assert ArcDataImageService.validate_image_tag("v1.0")
        assert ArcDataImageService.validate_image_tag("v1") is False
        assert ArcDataImageService.validate_image_tag("v1 tag") is False
        assert ArcDataImageService.validate_image_tag("v1.0 tag") is False

    def test_imagetag_parsing(self):
        (major, minor, revision, label) = ArcDataImageService.parse_image_tag(
            "v1.2.3_2021-07-30"
        )
        assert major == 1
        assert minor == 2
        assert revision == 3
        assert label == "2021-07-30"

    def test_retry_decorator_success(self):
        retryCount = 0

        @retry_method(
            retry_count=5,
            retry_delay=0.1,
            retry_method_description="retry test",
            retry_on_exceptions=(ValueError),
        )
        def retry_this():
            nonlocal retryCount
            retryCount += 1
            if retryCount < 4:
                raise ValueError("Should fail")
            return "Retried {0} times".format(retryCount)

        results = retry_this()
        assert results == "Retried 4 times"

    def test_retry_decorator_failed(self):
        @retry_method(
            retry_count=5,
            retry_delay=0.1,
            retry_method_description="retry test",
            retry_on_exceptions=(ValueError),
        )
        def retry_this():
            raise ValueError("Should fail")

        try:
            retry_this()
            assert False
        except Exception as e:
            assert (
                "Failed to retry test after retrying for 0 minute(s)." == str(e)
            )
