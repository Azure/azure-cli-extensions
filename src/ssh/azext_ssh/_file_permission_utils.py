import win32security
import ntsecuritycon as con
import getpass

def _set_certificate_permissions(path):
    """
    Returns the security descriptor of the file at the given path.
    """
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