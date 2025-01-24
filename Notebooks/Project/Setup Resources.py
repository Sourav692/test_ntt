# Databricks notebook source
# MAGIC %md
# MAGIC # This notebook creates Schemas for the Medallion Layers
# MAGIC

# COMMAND ----------

# MAGIC %pip install pyyaml
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,Initial Imports
import sys
import yaml
import os


# COMMAND ----------

dbutils.widgets.text("env_prefix", "dev", "Env: (dev/uat/prd)")
dbutils.widgets.text("catalog_name", "mycatalog", "Catalog Name")
dbutils.widgets.text("mode", "snapshot", "Catalog Name")
env_prefix = dbutils.widgets.get("env_prefix")
mode = dbutils.widgets.get("mode")

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

for catalog_config in master_config:
    catalog_owner = catalog_config["catalog_owner"]
    catalog_name = catalog_config["catalog_name"]
    group_folder = catalog_config["group_folder"]
    raw_storage_account_name, enriched_storage_account_name = get_storage_prefixes(f"{storage_config_path}{env_prefix}.yaml", group_folder)
    projects = catalog_config["projects"]

    for project_name in projects:
        print(f"project name is {project_name}")
        medallion_layers = projects[project_name]["schemas"].split(",")
        for layer in medallion_layers:
            if layer.lower() == "bronze":
                database_name = f"`{env_prefix}_{catalog_name}`.`{project_name}_bronze`"
                # Check if the bronze database already exists
                if spark.catalog.databaseExists(database_name):
                    print(f"{database_name} already exists")
                else:
                    dbutils.notebook.run(
                        "Medallion_Layer_Resources", 
                        0, 
                        {
                            "env_prefix": env_prefix,
                            "catalog_name": catalog_name,
                            "project_name": project_name, 
                            "medallion_layer": "bronze", 
                            "storage_account_name": raw_storage_account_name
                        }
                    )
            elif layer.lower() == "silver":
                database_name = f"`{env_prefix}_{catalog_name}`.`{project_name}_silver`"
                # Check if the silver database already exists
                if spark.catalog.databaseExists(database_name):
                    print(f"{database_name} already exists")
                else:
                    dbutils.notebook.run(
                        "Medallion_Layer_Resources", 
                        0, 
                        {
                            "env_prefix": env_prefix,
                            "catalog_name": catalog_name,
                            "project_name": project_name, 
                            "medallion_layer": "silver", 
                            "storage_account_name": raw_storage_account_name
                        }
                    )
                print(f"elem is {layer}")
            elif layer.lower() == "gold":
                database_name = f"`{env_prefix}_{catalog_name}`.`{project_name}_gold`"
                # Check if the gold database already exists
                if spark.catalog.databaseExists(database_name):
                    print(f"{database_name} already exists")
                else:
                    dbutils.notebook.run(
                        "Medallion_Layer_Resources", 
                        0, 
                        {
                            "env_prefix": env_prefix,
                            "catalog_name": catalog_name,
                            "project_name": project_name, 
                            "medallion_layer": "gold", 
                            "storage_account_name": raw_storage_account_name
                        }
                    )
            else:
                print(f"elem is {layer}")