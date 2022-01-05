import string
import random

# Env setup_scenario
def setup_scenario(test):
    randomString = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 5))
    test.kwargs.update({
        "serviceRG": "CLIUnitTest",
        "sqlMigrationService": "dmsCliUnitTest",
        "location": "eastus2euap",
        "createSqlMigrationService": "sqlServiceUnitTest"+randomString
    }),
    test.kwargs.update({
        "miRG": "migrationTesting",
        "managedInstance": "migrationtestmi",
        "miTargetDb": "tsum-CLI-MIOnline"
    }),
    test.kwargs.update({
        "vmRG": "tsum38RG",
        "virtualMachine": "DMSCmdletTest-SqlVM",
        "vmTargetDb": "tsum-Db-VM"
    })


#Test Cases
def step_sql_service_create(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-service create '
             '--location "{location}" '
             '--resource-group "{serviceRG}" '
             '--name "{createSqlMigrationService}"',
             checks=checks)

def step_sql_service_show(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-service show '
             '--resource-group "{serviceRG}" '
             '--name "{sqlMigrationService}"',
             checks=checks)

def step_sql_service_list_rg(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-service list '
             '--resource-group "{serviceRG}"',
             checks=checks)

def step_sql_service_list_sub(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-service list ',
             checks=checks)

def step_sql_service_list_migration(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-service list-migration '
             '--resource-group "{serviceRG}" '
             '--name "{sqlMigrationService}"',
             checks=checks)

def step_sql_service_list_auth_key(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-service list-auth-key '
             '--resource-group "{serviceRG}" '
             '--name "{sqlMigrationService}"',
             checks=checks)

def step_sql_service_regenerate_auth_key(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-service regenerate-auth-key '
             '--key-name "authKey1" '
             '--resource-group "{serviceRG}" '
             '--name "{sqlMigrationService}"',
             checks=checks)

def step_sql_service_list_integration_runtime_metric(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-service list-integration-runtime-metric '
             '--resource-group "{serviceRG}" '
             '--name "{sqlMigrationService}"',
             checks=checks)

def step_sql_service_delete(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-service delete -y '
             '--resource-group "{serviceRG}" '
             '--name "{createSqlMigrationService}"',
             checks=checks)

def step_to_sql_managed_instance_show(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration to-sql-managed-instance show '
             '--managed-instance-name "{managedInstance}" '
             '--resource-group "{miRG}" '
             '--target-db-name "{miTargetDb}"',
             checks=checks)

def step_to_sql_vm_show(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration to-sql-vm show '
             '--resource-group "{vmRG}" '
             '--sql-vm-name "{virtualMachine}" '
             '--target-db-name "{vmTargetDb}"',
             checks=checks)

# Env cleanup_scenario
def cleanup_scenario(test):
    pass


# Testcase: Scenario
def call_scenario(test):
    setup_scenario(test)
    try:
        step_sql_service_create(test, checks=[
            test.check("location", "{location}", case_sensitive=False),
            test.check("name", "{createSqlMigrationService}", case_sensitive=False),
            test.check("provisioningState", "Succeeded", case_sensitive=False)
        ])
        step_sql_service_show(test, checks=[
            test.check("location", "{location}", case_sensitive=False),
            test.check("name", "{sqlMigrationService}", case_sensitive=False)
        ])
        step_sql_service_list_rg(test)
        step_sql_service_list_sub(test)
        step_sql_service_list_migration(test)
        step_sql_service_list_auth_key(test)
        step_sql_service_regenerate_auth_key(test)
        step_sql_service_list_integration_runtime_metric(test, checks=[
            test.check("name", "default-ir", case_sensitive=False)
        ])
        step_sql_service_delete(test)
        step_to_sql_managed_instance_show(test, checks=[
            test.check("name", "{miTargetDb}", case_sensitive=False),
            test.check("type", "Microsoft.DataMigration/databaseMigrations", case_sensitive=False),
            test.check("properties.kind", "SqlMi", case_sensitive=False)
        ])
        step_to_sql_vm_show(test, checks=[
            test.check("name", "{vmTargetDb}", case_sensitive=False),
            test.check("type", "Microsoft.DataMigration/databaseMigrations", case_sensitive=False),
            test.check("properties.kind", "SqlVm", case_sensitive=False)
        ])
    except Exception as e:
        raise e
    finally:
        cleanup_scenario(test)