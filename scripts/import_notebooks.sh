#!/bin/bash

# Set the target workspace directory
TARGET_WORKSPACE_DIR="/Workspace/changed_config"

# # Step 1: Delete the target workspace directory if it exists
# echo "Deleting existing directory: $TARGET_WORKSPACE_DIR"
# databricks workspace delete PATH "$TARGET_WORKSPACE_DIR" --recursive || echo "Directory $TARGET_WORKSPACE_DIR may not exist, continuing..."


echo "Importing files into: $TARGET_WORKSPACE_DIR"
databricks workspace import-dir ./changed_files_output/ "$TARGET_WORKSPACE_DIR" --overwrite

echo "Finished deleting and importing files into Databricks workspace."