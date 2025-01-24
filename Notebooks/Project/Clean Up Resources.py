# Databricks notebook source
dbutils.widgets.text("env_prefix", "dev", "Env: (dev/uat/prd)")
dbutils.widgets.text("catalog_name", "mycatalog", "Catalog Name")
dbutils.widgets.text("project_name", "tis_supportlogic", "Project Name")
env_prefix = dbutils.widgets.get("env_prefix")
catalog_name = dbutils.widgets.get("catalog_name")
project_name = dbutils.widgets.get("project_name")

# COMMAND ----------

# MAGIC %sql
# MAGIC Select '${env_prefix}_${catalog_name}.${project_name}_x' as PROJECT_TO_BE_DROPPED;

# COMMAND ----------

# MAGIC %sql
# MAGIC use catalog ${env_prefix}_${catalog_name};
# MAGIC DROP SCHEMA if exists ${project_name}_bronze CASCADE;
# MAGIC DROP SCHEMA if exists ${project_name}_silver CASCADE;
# MAGIC DROP SCHEMA if exists ${project_name}_gold CASCADE;

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP EXTERNAL LOCATION IF EXISTS ${env_prefix}_${catalog_name}_${project_name}_bronze FORCE;
# MAGIC DROP EXTERNAL LOCATION IF EXISTS ${env_prefix}_${catalog_name}_${project_name}_silver FORCE;
# MAGIC DROP EXTERNAL LOCATION IF EXISTS ${env_prefix}_${catalog_name}_${project_name}_gold FORCE;