# Databricks notebook source
# MAGIC %md
# MAGIC # This notebook deletes the catalog and its external location. i.e. dev_mycatalog

# COMMAND ----------

dbutils.widgets.text("env_prefix", "dev", "Env: (dev/uat/prd)")
dbutils.widgets.text("catalog_name", "mycatalog", "Catalog Name")

# COMMAND ----------

# MAGIC %sql
# MAGIC Select '${env_prefix}_${catalog_name}' as CATALOG_TO_BE_DROPPED;

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP SCHEMA IF EXISTS ${env_prefix}_${catalog_name}.default CASCADE;
# MAGIC DROP CATALOG IF EXISTS ${env_prefix}_${catalog_name};

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP EXTERNAL LOCATION IF EXISTS ${env_prefix}_${catalog_name} FORCE;

# COMMAND ----------

