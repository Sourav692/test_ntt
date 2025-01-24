# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC ## Initial Imports

# COMMAND ----------

# MAGIC %pip install pyyaml
# MAGIC !pip install databricks-sdk
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

host = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().getOrElse(None)
token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().getOrElse(None)

# COMMAND ----------

from databricks.sdk import WorkspaceClient
from databricks.sdk.service import workspace,iam
from databricks.sdk.service.iam import ComplexValue
from databricks.sdk.service.workspace import AzureKeyVaultSecretScopeMetadata,ScopeBackendType
import sys
import yaml
import os


os.environ['DATABRICKS_HOST']  = host
os.environ['DATABRICKS_TOKEN'] = token
w = WorkspaceClient()

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ### Utils Funcions

# COMMAND ----------

# Check if Scope Exists
def scope_exists(scope_name):
    if scope_name in list(map(lambda x: x.as_dict()["name"],w.secrets.list_scopes())):
        return True
    else:
        return False
    
# Check if Group Exists
def group_exists(group_name):
    if group_name in list(map(lambda x: x.display_name,w.groups.list())):
        return True
    else:
        return False   
    
# Create Scope
def create_scope (scope_name,dns,resouceID):

    scope_metadata = AzureKeyVaultSecretScopeMetadata(
    dns_name = dns,
    resource_id = resouceID
    )
    w.secrets.create_scope(
    scope=scope_name,
    # scope_backend_type=ScopeBackendType.AZURE_KEYVAULT,
    backend_azure_keyvault=scope_metadata)

# Grant a group permissions on the secret scope
def process_scope_permissions(scope_config):
    scopes = scope_config['scope_group_mapping']
    for scope, mappings in scopes.items():
        if scope_exists(scope):
            print(f"Scope: {scope} exists")
            for mapping in mappings:
                group_name = mapping['name']
                role = mapping['permission']
                if role.lower() == "manage":
                    permission = workspace.AclPermission.MANAGE
                else:
                    permission = workspace.AclPermission.READ
                if group_exists(group_name):
                    print(f"Group {group_name} exists.Assigning the {role} permission to scope {scope}")
                    w.secrets.put_acl(scope=scope, permission=permission, principal=group_name)
                else:
                    print(f"Group {group_name} does not exists. Permission Assignment is not possible")
        else:
            print(f"Scope {scope} does not exists")

        print()

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ### Read Config File

# COMMAND ----------

import os
root_path = "/Workspace" + os.path.dirname(dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get().split("Notebooks")[0])
config_path = root_path + "/Scope_Configs/"
sys.path.append(config_path)

# COMMAND ----------

with open(f"{config_path}scope.yaml", "r") as file:
    config_value = yaml.safe_load(file)

# COMMAND ----------

scopes = config_value["scope_list"]
group_list = config_value["group_list"].split(",")
scope_group_mapping = config_value["scope_group_mapping"]

# COMMAND ----------

# MAGIC %md
# MAGIC ### Iterate Over scope_list and Create the scopes which do not exists

# COMMAND ----------

#TODO - Iterate Over scope_list and Create the scopes which do not exists

scopes_list = list(scopes.keys())

for key,value in scopes.items():
    scope_name = key
    if scope_exists(scope_name):
        print(f"Scope {scope_name} exists")
    else:
        print(f"Scope {scope_name} does not exists. Creating the scope")
        dns_name = value["dns_name"]
        resource_id = value["resource_id"]
        create_scope(scope_name, dns_name, resource_id)

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ### Grant a group permissions on the secret scope

# COMMAND ----------

process_scope_permissions(config_value)

# COMMAND ----------

