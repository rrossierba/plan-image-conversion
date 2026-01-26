import json
from src.convert import convert_blocksworld_plans

def run():
    config_path = 'files/config.json'

    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    plan_path = config.get("plan_path")
    format = config.get("format", "png")
    save_path = config.get("save_path")
    convert_blocksworld_plans(plan_path, format, save_path)

if __name__ == "__main__":
    run()