# Databricks notebook source
# MAGIC %md
# MAGIC # This notebook creates the catalog and its external location. i.e. dev_mycatalog
# MAGIC # Catalog name needs to match the container name in the datalake with prefix 'lakehouse'. i.e. lakehouse-mycatalog
# MAGIC

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
dbutils.widgets.text("mode", "snapshot", "Catalog Name")
env_prefix = dbutils.widgets.get("env_prefix")
mode = dbutils.widgets.get("mode")

# COMMAND ----------


root_path = "/Workspace" + os.path.dirname(dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get().split("Notebooks")[0])
common_utils_path = root_path + "/Notebooks/Common"
catalog_config_path = root_path + "/Catalog_Configs/"
changed_config_path = root_path +"/changed_config/config.yml"
sys.path.append(common_utils_path)
sys.path.append(catalog_config_path)

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



# COMMAND ----------

from utils import *

# COMMAND ----------

catalog_config_path

# COMMAND ----------

# catalog_config_value, group_folder = get_catalog_config(catalog_config_path, catalog_name)

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
    location = spark.sql(f"DESCRIBE CATALOG EXTENDED {env_prefix}_sn_databricks").filter("info_name = 'Storage Root'").select("info_value").head()[0]
    root_path = location[:location.rfind('/')]
    # Create Exteral Location for Catalog
    spark.sql(f"""
        CREATE EXTERNAL LOCATION IF NOT EXISTS {env_prefix}_{catalog_name}
        URL '{root_path}/{env_prefix}_{catalog_name}'
        WITH (STORAGE CREDENTIAL {env_prefix}_sn_databricks)
        COMMENT 'External location for Catalog {env_prefix}_{catalog_name}';
        """)
    # Create Catalog
    spark.sql(f"""
        CREATE CATALOG IF NOT EXISTS {env_prefix}_{catalog_name}
        MANAGED LOCATION '{root_path}/{env_prefix}_{catalog_name}'
        """)
    
    # Setting up Permission for Catalog
    if catalog_owner != None and catalog_owner !="":
        spark.sql(f"""
        ALTER EXTERNAL LOCATION `{env_prefix}_{catalog_name}` OWNER TO `{catalog_owner}`
        """)
    else:
        print("No operation")


# COMMAND ----------

# %sql
# Select '${env_prefix}_${catalog_name}' as CATALOG_TO_BE_CREATED;

# COMMAND ----------

# location = spark.sql(f"DESCRIBE CATALOG EXTENDED {env_prefix}_sn_databricks").filter("info_name = 'Storage Root'").select("info_value").head()[0]
# root_path = location[:location.rfind('/')]
# spark.conf.set("path.root", root_path)

# COMMAND ----------

# %sql
# CREATE EXTERNAL LOCATION IF NOT EXISTS ${env_prefix}_${catalog_name}
# URL '${path.root}/${env_prefix}_${catalog_name}'
# WITH (STORAGE CREDENTIAL ${env_prefix}_sn_databricks)
# COMMENT 'External location for Catalog ${env_prefix}_${catalog_name}';

# COMMAND ----------

# %sql
# CREATE CATALOG IF NOT EXISTS ${env_prefix}_${catalog_name}
#   MANAGED LOCATION '${path.root}/${env_prefix}_${catalog_name}';

# COMMAND ----------

# MAGIC %md
# MAGIC Setting permissions on Location & Catalog

# COMMAND ----------

# print (catalog_owner)
# if catalog_owner != None and catalog_owner !="":
#     spark.sql(f"""
#     ALTER EXTERNAL LOCATION `{env_prefix}_{catalog_name}` OWNER TO `{catalog_owner}`
#     """)
# else:
#     print("No operation")

# COMMAND ----------

