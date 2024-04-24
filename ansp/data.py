import json
import os

def create_json(config_file_path = 'runs/run_config.json'):
    """
    create json file in runs/run_config.json with the number of current run set to zero
    """
    # Create the configuration dictionary
    config = {"run_number": 0}

    # Open the JSON file for writing
    with open(config_file_path, 'w') as f:
        # Convert the dictionary to a JSON string and write it to the file
        json.dump(config, f)

def get_run_number(config_file_path = 'runs/run_config.json'):
    # Load the configuration file
    with open(config_file_path, 'r') as f:
        config = json.load(f)

    # Load the configuration file
    with open(config_file_path, 'r') as f:
        config = json.load(f)

    # Increment the run number
    return config['run_number']

def increment_run(config_file_path = 'runs/run_config.json'):
    # Create file if doesn't exist yet
    if not os.path.isfile(config_file_path):
        create_json(config_file_path)

    # Load the configuration file
    with open(config_file_path, 'r') as f:
        config = json.load(f)

    # Increment the run number
    config['run_number'] += 1

    # Save the updated configuration file
    with open(config_file_path, 'w') as f:
        json.dump(config, f)
