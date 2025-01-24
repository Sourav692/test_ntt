# Databricks notebook source
dbutils.widgets.text("storage_account_name", "", "Storage Account Name")
dbutils.widgets.text("env_prefix", "dev", "Env: (dev/uat/prd)")
dbutils.widgets.text("catalog_name", "mycatalog", "Catalog Name")
dbutils.widgets.text("project_name", "tis_supportlogic", "Project Name")
dbutils.widgets.text("medallion_layer", "bronze", "Medallion Layer: bronze/silver/gold")

# COMMAND ----------

# MAGIC %md
# MAGIC # resources

# COMMAND ----------

catalog_name = dbutils.widgets.get("catalog_name")
container_name = f'lakehouse-{catalog_name.replace("_", "-")}'
print(container_name)
spark.conf.set("path.container_name", container_name)

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'abfss://${path.container_name}@${storage_account_name}.dfs.core.windows.net/${project_name}/${medallion_layer}' as location

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE EXTERNAL LOCATION IF NOT EXISTS ${env_prefix}_${catalog_name}_${project_name}_${medallion_layer}
# MAGIC URL 'abfss://${path.container_name}@${storage_account_name}.dfs.core.windows.net/${project_name}/${medallion_layer}'
# MAGIC WITH (STORAGE CREDENTIAL ${env_prefix}_datalake_credential)
# MAGIC COMMENT 'External location for ${env_prefix}_${catalog_name}.${project_name}_${medallion_layer}';

# COMMAND ----------

# MAGIC %sql
# MAGIC use catalog ${env_prefix}_${catalog_name};
# MAGIC create schema if not exists ${project_name}_${medallion_layer}
# MAGIC managed location 'abfss://${path.container_name}@${storage_account_name}.dfs.core.windows.net/${project_name}/${medallion_layer}'