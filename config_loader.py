import yaml
import os

def get_config(file_path="config.yaml"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"\n[ERROR] Config file '{file_path}' not found!\n"
            f"Please create it in the root directory of the project."
        )
        
    with open(file_path, "r") as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            raise ValueError(f"[ERROR] Failed to parse YAML in {file_path}: {exc}")

    if config is None:
        raise ValueError(f"[ERROR] Config file '{file_path}' is empty!")

    REQUIRED_KEYS = [
        'images_path', 
        'labels_path', 
        'geom_path'
    ]

    missing_keys = []
    empty_keys = []

    for key in REQUIRED_KEYS:
        if key not in config:
            missing_keys.append(key)
        elif config[key] is None or str(config[key]).strip() == "":
            empty_keys.append(key)

    if missing_keys or empty_keys:
        error_msg = "\n" + "="*50 + "\n"
        error_msg += "CONFIG VALIDATION FAILED:\n"
        
        if missing_keys:
            error_msg += f" - MISSING KEYS: {', '.join(missing_keys)}\n"
        
        if empty_keys:
            error_msg += f" - EMPTY VALUES IN: {', '.join(empty_keys)}\n"
            
        error_msg += "\nPlease check your config.yaml and fill in the paths.\n"
        error_msg += "="*50
        raise KeyError(error_msg)

    return config