from azure.mgmt.servicebus.models.service_bus_management_client_enums import SkuName, SkuTier, AccessRights, KeyType

def skunameconverter(skuname):

    if(skuname=='Basic'):
        return SkuName.basic
    if (skuname == 'Standard'):
        return SkuName.standard
    if (skuname == 'Premium'):
        return SkuName.premium

def skutireconverter(skutire):

    if(skutire=='Basic'):
        return SkuTier.basic
    if (skutire == 'Standard'):
        return SkuTier.standard
    if (skutire == 'Premium'):
        return SkuTier.premium

def accessrights_converter(accesrights):

     if(len(accesrights) > 0):
         for index in range(len(accesrights)):
             if(accesrights[index] == 'Send'):
                 accesrights[index] = AccessRights.send
             if(accesrights[index] == 'Manage'):
                 accesrights[index] = AccessRights.manage
             if (accesrights[index] == 'Listen'):
                 accesrights[index] = AccessRights.listen
         return accesrights
