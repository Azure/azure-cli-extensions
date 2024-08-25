import win32security
import ntsecuritycon as con
import platform
import os

def set_certificate_permissions(path):
    if platform.system() != 'Windows':
        os.chmod(path, 0o644)
        return

    sd = win32security.GetFileSecurity(
        path,
        win32security.DACL_SECURITY_INFORMATION
    )

    admSid = win32security.LookupAccountName("", "Administrators")[0]
    systemSid = win32security.LookupAccountName("", "SYSTEM")[0]
    ownerSid = _get_owner_string(path)

    dacl = win32security.ACL()

    dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, admSid)
    dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, systemSid)
    dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, ownerSid)

    sd.SetSecurityDescriptorDacl(1, dacl, 0)
    win32security.SetFileSecurity(path, win32security.DACL_SECURITY_INFORMATION, sd)

    
def _get_owner_string(path):
    sd = win32security.GetFileSecurity(path, win32security.OWNER_SECURITY_INFORMATION)
    return sd.GetSecurityDescriptorOwner()