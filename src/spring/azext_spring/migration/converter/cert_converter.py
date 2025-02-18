import re

from .base_converter import ConverterTemplate

# Concrete Converter Subclass for certificate
class CertConverter(ConverterTemplate):
    def load_source(self, source):
        self.source = source
        print(f"Cert source: {self.source}")

    def calculate_data(self):
        certName = self.source['name'].split('/')[-1]
        moduleName = "cert_" + certName.replace("-", "_")
        isKeyVaultCert = False
        certKeyVault = self._get_cert_key_vault()

        self.data = {
            "certName": certName,
            "moduleName": moduleName,
            "certificateType": "ServerSSLCertificate",
        }

        if certKeyVault:
            self.data["certificateKeyVaultProperties"] = certKeyVault
            isKeyVaultCert = True
        else:
            self.data["value"] = "*"
            isKeyVaultCert = False
        self.data["isKeyVaultCert"] = isKeyVaultCert
        print(f"cert data: {self.data}")

    def get_template_name(self):
        return "cert.bicep"
    
    def _get_cert_key_vault(self):
        certKeyVault = None
        if self.source['properties'].get('type') == "KeyVaultCertificate":
            if self.source['properties'].get('vaultUri') and self.source['properties'].get('keyVaultCertName'):
                certKeyVault = {
                    "keyVaultUrl": self.source['properties']['vaultUri'] + "/secrets/" + self.source['properties']['keyVaultCertName'],
                    "identity": "system"
                }
        return certKeyVault
