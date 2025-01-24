# Databricks notebook source
# MAGIC %md
# MAGIC This notebook does a dry run by default. Change the value to False to actually assign the permissions.
# MAGIC - Admin role:
# MAGIC   - The team has ALL PRIVILEGES on all three schemas.
# MAGIC   - The team owns the all three external locations.
# MAGIC - Engineer role:
# MAGIC   - The team has ALL PRIVILEGES on all three schemas.
# MAGIC - Analyst role:
# MAGIC   - The team has SELECT on all three schemas.

# COMMAND ----------

# MAGIC %pip install pyyaml
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

import sys
import yaml
import os

# COMMAND ----------

dbutils.widgets.text("env_prefix", "dev", "Env: (dev/uat/prd)")
dbutils.widgets.text("catalog_name", "mycatalog", "Catalog Name")
dbutils.widgets.text("mode", "incremental", "Mode")
dbutils.widgets.text("dry_run", "true")
env_prefix = dbutils.widgets.get("env_prefix")
mode = dbutils.widgets.get("mode")
dry_run = dbutils.widgets.get("dry_run")

# COMMAND ----------

root_path = "/Workspace" + os.path.dirname(dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get().split("Notebooks")[0])
common_utils_path = root_path + "/Notebooks/Common"
catalog_config_path = root_path + "/Catalog_Configs/"
storage_config_path = root_path + "/Storage_Configs/"
changed_config_path = root_path +"/changed_config/config.yml"
sys.path.append(common_utils_path)
sys.path.append(catalog_config_path)
sys.path.append(storage_config_path)

# COMMAND ----------

catalog_names = []
if mode.lower() == "snapshot":
    print("Snapshot Mode is selected. Read the catalog names from the widget")
    catalog_names = dbutils.widgets.get("catalog_name").split(",")
elif mode.lower() == "full":
    print("Full Mode is selected. Read the catalog names from the catalog_config folder")
    for root, dirs, files in os.walk(catalog_config_path):
        for file in files:
            if file.endswith(".yaml"):
                catalog = file.split(".")[0]
                catalog_names.append(catalog)

elif mode.lower() == "incremental":
    print("Incremental Mode is selected. Read the catalog names from the changed_config file") 
    # changed_config_file = "/Workspace/changed_config/changed_config.yml"
    with open(changed_config_path, 'r') as file:
        lines = file.readlines()
    formatted_content = ', '.join(line.strip() for line in lines)
    changed_config = formatted_content.split(",")
    for elem in changed_config:
        catalog = elem.split("/")[-1].split(".")[0]
        catalog_names.append(catalog)
else:
    print("Invalid Mode")
    dbutils.notebook.exit()
print(catalog_names)

# COMMAND ----------

from utils import *

# COMMAND ----------

master_config = []
for catalog_name in catalog_names:
    catalog_config, group_folder = get_catalog_config(catalog_config_path, catalog_name)
    catalog_config["group_folder"] = group_folder
    catalog_config["catalog_name"] = catalog_name
    master_config.append(catalog_config)

print(master_config)

# COMMAND ----------

is_dry_run = dry_run.lower() == "true"

# COMMAND ----------

for catalog_config in master_config:
    catalog_owner = catalog_config["catalog_owner"]
    catalog_name = catalog_config["catalog_name"]
    group_folder = catalog_config["group_folder"]
    raw_storage_account_name, enriched_storage_account_name = get_storage_prefixes(f"{storage_config_path}{env_prefix}.yaml", group_folder)
    projects = catalog_config["projects"]

    for project, values in projects.items():
        project_name = project
        layers = values.get("schemas", "").split(",")
        
        for team_role, name in values.get("roles", {}).items():
            if not name:  # Skip if team name is None or empty
                continue
            
            team_name_list = name.split(",")
            is_admin = team_role.lower() == "admins"
            is_engineer = team_role.lower() == "engineers"
            is_analyst = team_role.lower() == "analysts"
            
            for team_name in team_name_list:
                print(f"{team_name} has {team_role} role")
                
                # Grant USE CATALOG privilege
                grant_catalog_query = f'GRANT USE CATALOG ON CATALOG {env_prefix}_{catalog_name} TO `{team_name}`'
                if is_dry_run:
                    print(grant_catalog_query)
                else:
                    spark.sql(grant_catalog_query)
                
                # Determine privileges for schema access
                privileges = "SELECT" if is_analyst else "ALL PRIVILEGES"
                for layer in layers:
                    if is_admin:
                        # Grant OWNER privilege for external location
                        location_privilege_query = f'ALTER EXTERNAL LOCATION {env_prefix}_{catalog_name}_{project_name}_{layer} OWNER TO `{team_name}`'
                        if is_dry_run:
                            print(location_privilege_query)
                        else:
                            spark.sql(location_privilege_query)
                    
                    if is_analyst:
                        # Grant USE SCHEMA privilege for analysts
                        schema_privilege_query1 = f'GRANT USE SCHEMA ON SCHEMA {env_prefix}_{catalog_name}.{project_name}_{layer} TO `{team_name}`'
                        if is_dry_run:
                            print(schema_privilege_query1)
                        else:
                            spark.sql(schema_privilege_query1)
                    
                    # Grant privileges on schema (SELECT or ALL PRIVILEGES)
                    schema_privilege_query2 = f'GRANT {privileges} ON SCHEMA {env_prefix}_{catalog_name}.{project_name}_{layer} TO `{team_name}`'
                    if is_dry_run:
                        print(schema_privilege_query2)
                    else:
                        spark.sql(schema_privilege_query2)
                    
                    print('-------')


# COMMAND ----------

