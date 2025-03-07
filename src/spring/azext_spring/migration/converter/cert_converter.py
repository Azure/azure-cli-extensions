from knack.log import get_logger
from .base_converter import BaseConverter

logger = get_logger(__name__)

# Concrete Converter Subclass for certificate
class CertConverter(BaseConverter):

    def __init__(self, source):
        def transform_data():
            asa_content_certs = self.wrapper_data.get_content_certificates()
            for cert in asa_content_certs:
                logger.warning(f"Mismatch: The content certificate: {cert['name']} cannot be exported automatically. Please export it manually.")
            return self.wrapper_data.get_certificates()
        super().__init__(source, transform_data)

    def transform_data_item(self, cert):
        certName = cert['name'].split('/')[-1]
        isKeyVaultCert = False
        cert = {
            "certName": certName,
            "moduleName": self._get_cert_module_name(cert),
            "certificateType": "ServerSSLCertificate",
        }
        certKeyVault = self._get_cert_key_vault(cert)
        if certKeyVault:
            cert["certificateKeyVaultProperties"] = certKeyVault
            isKeyVaultCert = True
        else:
            cert["value"] = "*"
            isKeyVaultCert = False
        cert["isKeyVaultCert"] = isKeyVaultCert
        return cert        

    def get_template_name(self):
        return "cert.bicep"
    
    def _get_cert_key_vault(self, cert):
        certKeyVault = None
        if cert['properties'].get('type') == "KeyVaultCertificate":
            if cert['properties'].get('vaultUri') and cert['properties'].get('keyVaultCertName'):
                certKeyVault = {
                    "keyVaultUrl": cert['properties']['vaultUri'] + "/secrets/" + cert['properties']['keyVaultCertName'],
                    "identity": "system"
                }
        return certKeyVault
