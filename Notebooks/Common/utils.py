import os
import yaml

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def find_catalog_file(base_path, catalog_name):
    """Search for a catalog file in all subdirectories."""
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file == f"{catalog_name}.yaml":
                return os.path.join(root, file), os.path.basename(root)  # Return file path and group folder
    return None, None

def get_storage_prefixes(storage_config_path, group_name):
    """
    Retrieve raw and enriched storage prefixes for a given group.
    """
    storage_config = load_yaml(storage_config_path)
    if 'groups' in storage_config['Storage'] and group_name in storage_config['Storage']['groups']:
        group_storage = storage_config['Storage']['groups'][group_name]
        return group_storage['rawStorage'], group_storage['enrichedStorage']
    else:
        raise ValueError(f"Storage configuration for group '{group_name}' not found.")

def get_catalog_config(catalog_base_path, catalog_name):
    """
    Retrieve catalog configuration by finding and loading its YAML file.
    """
    catalog_file, group_folder = find_catalog_file(catalog_base_path, catalog_name)
    catalog_config = load_yaml(catalog_file)
    return catalog_config, group_folder
