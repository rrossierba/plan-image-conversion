import json
from src.convert import *

def run():
    config_path = 'files/config.json'

    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    # load configuration parameters
    domain = config.get('domain')

    plan_collection_path = config.get('plan_collection_path')
    problem_path = config.get('problem_folder')
    animation_profile_path = config.get('animation_profile_path')    
    format = config.get('format')
    save_path = config.get('save_path')
    save_path = f'{save_path}/{domain}'

    domain_file_path = config.get('domain_file_path')

    if domain == 'blocksworld':
        converter = BlocksWorldConverter(
            domain_path=domain_file_path,
            problem_path=problem_path,
            plan_path=plan_collection_path,
            animation_profile_path= animation_profile_path,
            format=format,
            save_path=save_path
            )
    else:
        raise NotImplementedError('Requested domain is not implemented yet')
    
    converter.convert_plans()

if __name__ == '__main__':
    run()