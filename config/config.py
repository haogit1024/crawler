import json


def get_config_params():
    with open('config.json') as f:
        json_str = f.read()
        config = json.load(json_str)
        return config
