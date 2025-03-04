import ujson

CONFIG_PATH = "/src/data/config.json"

def import_config(configPath = CONFIG_PATH):
    with open(configPath, "r") as file:
        return ujson.load(file)  # Parse JSON file into a dictionary


def export_config(config,configPath = CONFIG_PATH):
    with open(configPath, "w") as file:
        ujson.dump(config, file)
        
def get_rawConfig(configPath = CONFIG_PATH):
    with open(configPath, "r") as file:
        return file.read()