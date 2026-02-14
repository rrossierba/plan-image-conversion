import json
from src.convert import *
from src.vfg_plan import *
from src.visualizer import *

def run():
    config_path = 'files/config.json'

    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    # load configuration parameters
    domain = config.get('domain')

    # create variables for config params
    plan_collection_path = config.get('plan_collection_path')
    problem_path = config.get('problem_folder')
    animation_profile_path = config.get('animation_profile_path')    
    format = config.get('format', 'png')
    save_path = config.get('save_path')
    domain_file_path = config.get('domain_file_path')
    n_jobs = config.get('num_processes', 1)

    # implemented domains: blocksworld, logistics (...)
    if domain == 'blocksworld':
        visualizer_class=BlocksWorldVisualizer
        vfg_plan_class=BlocksWorldVfgPlan
        name_parser = blocksworld_problem_name_parser
    elif domain =='logistics':
        visualizer_class=LogisticsVisualizer
        vfg_plan_class=BlocksWorldVfgPlan
        name_parser = blocksworld_problem_name_parser
    else:
        raise NotImplementedError('Requested domain is not implemented yet')
    
    # run the actual conversion
    GenericConverter(
        domain_path=domain_file_path,
        problem_path=problem_path,
        plan_path=plan_collection_path,
        animation_profile_path=animation_profile_path,
        format=format,
        save_path=save_path,
        visualizer_class=visualizer_class,
        vfg_plan_class= vfg_plan_class,
        n_jobs=n_jobs,
        name_parser=name_parser
    ).convert_plans()

if __name__ == '__main__':
    run()