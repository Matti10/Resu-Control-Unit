try:
    import ujson as json
except:
    import json

CONFIG_PATH = "/data/config.json"


def import_config(configPath=CONFIG_PATH):
    with open(configPath, "r") as file:
        return json.load(file)  # Parse JSON file into a dictionary


def export_config(config, configPath=CONFIG_PATH):
    with open(configPath, "w") as file:
        json.dump(config, file)


def get_rawConfig(configPath=CONFIG_PATH):
    with open(configPath, "r") as file:
        return file.read()
