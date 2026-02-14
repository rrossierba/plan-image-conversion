import json
import argparse
import os
import sys
import logging
from src.convert import GenericConverter, blocksworld_problem_name_parser, logistics_problem_name_parser
from src.vfg_plan import BlocksWorldVfgPlan, LogisticsVfgPlan
from src.visualizer import BlocksWorldVisualizer, LogisticsVisualizer
from src.logger import setup_logging

# logging configuration
setup_logging()
logger = logging.getLogger(__name__)

# to extend to a new domain add the domain as the ones in the dictionary
DOMAIN_REGISTRY = {
    'blocksworld': {
        'visualizer': BlocksWorldVisualizer,
        'vfg_plan': BlocksWorldVfgPlan,
        'problem_name_parser': blocksworld_problem_name_parser
    },
    'logistics': { # still work in progress
        'visualizer': LogisticsVisualizer,
        'vfg_plan': LogisticsVfgPlan,
        'problem_name_parser': logistics_problem_name_parser
    }
}

def load_config(config_path):
    """Loads and validates the configuration file."""
    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found at: {config_path}")
        sys.exit(1)
        
    try:
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON configuration: {e}")
        sys.exit(1)

def run():
    parser = argparse.ArgumentParser(description="PDDL Plan to Image Converter")
    parser.add_argument('-c', '--config', help='Path of JSON configuration file')
    args = parser.parse_args()

    config_path = args.config if args.config else os.getenv('CONFIG_FILE', 'files/config.json')
    
    logger.info(f"Starting converter with config: {config_path}")
    config = load_config(config_path)

    domain_name = config.get('domain', '').lower().strip() # to avoid problems

    if domain_name not in DOMAIN_REGISTRY:
        logger.error(f"Domain '{domain_name}' is not implemented. Available domains: {list(DOMAIN_REGISTRY.keys())}")
        sys.exit(1)
    
    try:
        # parameters
        plan_collection_path = config.get('plan_collection_path')
        problem_path = config.get('problem_folder')
        animation_profile_path = config.get('animation_profile_path')    
        output_format = config.get('format', 'png')
        save_path = config.get('save_path')
        domain_file_path = config.get('domain_file_path')
        n_jobs = config.get('num_processes', 1)

        # create the converter
        domain_specific_args = DOMAIN_REGISTRY[domain_name]
        converter = GenericConverter(
            domain_path=domain_file_path,
            problem_path=problem_path,
            plan_path=plan_collection_path,
            animation_profile_path=animation_profile_path,
            format=output_format,
            save_path=save_path,
            visualizer_class=domain_specific_args['visualizer'],
            vfg_plan_class=domain_specific_args['vfg_plan'],
            n_jobs=n_jobs,
            name_parser=domain_specific_args['problem_name_parser']
        )
        logger.info(f"Initialization complete. Starting conversion for domain: {domain_name}")
        
        # start the conversion
        converter.convert_plans()
        logger.info("Conversion process finished.")

    except Exception as e:
        logger.critical(f"Error during execution: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    run()