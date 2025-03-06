from .base_converter import ConverterTemplate

# Concrete Converter Subclass for certificate
class CertConverter(ConverterTemplate):

    def __init__(self, input):
        def extract_data():
            certs = []
            asa_certs = self.wrapper_data.get_resources_by_type('Microsoft.AppPlatform/Spring/certificates')
            for cert in asa_certs:
                if cert['properties'].get('type') == "KeyVaultCertificate":
                    certs.append(cert)    
                elif cert['properties'].get('type') == "ContentCertificate":
                    certs.append(cert)
            return certs
        super().__init__(input, extract_data)

    def transform_data(self, cert):
        certName = cert['name'].split('/')[-1]
        moduleName = "cert_" + certName.replace("-", "_")
        isKeyVaultCert = False
        certKeyVault = self._get_cert_key_vault(cert)
        cert = {
            "certName": certName,
            "moduleName": moduleName,
            "certificateType": "ServerSSLCertificate",
        }
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
