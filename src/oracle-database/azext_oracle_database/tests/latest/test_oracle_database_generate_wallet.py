import base64
import os
import tempfile
import unittest
import zipfile
from types import SimpleNamespace

from azure.cli.core.azclierror import ValidationError

from azext_oracle_database.aaz.latest.oracle_database.autonomous_database._generate_wallet import GenerateWallet


class _ArgValue:

    def __init__(self, value):
        self.value = value

    def to_serialized_data(self):
        return self.value


class OracleDatabaseGenerateWalletTest(unittest.TestCase):

    def _create_command(self, result, file_path=None, autonomous_database_name="testadb"):
        command = object.__new__(GenerateWallet)
        command.ctx = SimpleNamespace(
            vars=SimpleNamespace(instance={}),
            args=SimpleNamespace(
                file=_ArgValue(file_path) if file_path else None,
                autonomousdatabasename=_ArgValue(autonomous_database_name),
            ),
        )
        command.deserialize_output = lambda *_, **__: result
        return command

    def _create_wallet_payload(self):
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            with zipfile.ZipFile(temp_path, "w") as wallet_zip:
                wallet_zip.writestr("tnsnames.ora", "test tnsnames")
                wallet_zip.writestr("sqlnet.ora", "test sqlnet")

            with open(temp_path, "rb") as wallet_file:
                return base64.b64encode(wallet_file.read()).decode("utf-8")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_generate_wallet_saves_zip_to_file_argument(self):
        wallet_files = self._create_wallet_payload()

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "wallet.zip")
            command = self._create_command({"walletFiles": wallet_files}, file_path=file_path)

            result = command._output()

            self.assertEqual(file_path, result["file"])
            self.assertTrue(zipfile.is_zipfile(file_path))
            with zipfile.ZipFile(file_path) as wallet_zip:
                self.assertIn("tnsnames.ora", wallet_zip.namelist())
                self.assertIn("sqlnet.ora", wallet_zip.namelist())

    def test_generate_wallet_saves_zip_to_default_file_name(self):
        wallet_files = self._create_wallet_payload()

        with tempfile.TemporaryDirectory() as temp_dir:
            current_dir = os.getcwd()
            os.chdir(temp_dir)
            try:
                command = self._create_command({"walletFiles": wallet_files}, autonomous_database_name="crdr0611")

                result = command._output()

                self.assertEqual("wallet-crdr0611.zip", result["file"])
                self.assertTrue(zipfile.is_zipfile("wallet-crdr0611.zip"))
            finally:
                os.chdir(current_dir)

    def test_generate_wallet_requires_wallet_files_content(self):
        command = self._create_command({})

        with self.assertRaises(ValidationError):
            command._output()


if __name__ == "__main__":
    unittest.main()
