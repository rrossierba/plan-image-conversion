import os, sys, re, gc, pickle, logging
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from multiprocessing import Pool
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
from typing import Type, Callable, Union, List
from logger import setup_logging

# need to be imported for the pickle objects
from plan import Plan
from vfg_plan import VfgPlan
from visualizer import Visualizer

setup_logging()
logger = logging.getLogger(__name__)

# global variables, instantiated just once but with global scope
g_domain_text:str = None
g_animation_profile_text:str = None
g_problem_path:str = None
g_result_folder_name:str = None
g_format:str = None
g_VisualizerClass:Type = None
g_VfgPlanClass:Type = None
g_name_parser:Callable[[str], str] = None

# initialize the global variables, useful for multi-processing tasks
def worker_initializer(domain_text, animation_profile_text, problem_path, 
                        folder_name, format, VisualizerClass, VfgPlanClass, parser):
    
    '''
    Initialize the global variables, useful for multi-processing tasks
    
    :param domain_text
    :param animation_profile_text
    :param problem_path
    :param folder_name
    :param format: format
    :param VisualizerClass: Visualizer class
    :param VfgPlanClass: VfgPlan class
    :param parser: function to correctely parse problem names
    '''
    
    global g_domain_text, g_animation_profile_text, g_problem_path, g_result_folder_name, g_format, g_VisualizerClass, g_VfgPlanClass, g_name_parser
    
    g_domain_text = domain_text
    g_animation_profile_text = animation_profile_text
    g_problem_path = problem_path
    g_result_folder_name = folder_name
    g_format = format
    g_VisualizerClass = VisualizerClass
    g_VfgPlanClass = VfgPlanClass
    g_name_parser = parser
    
    setup_logging()
    gc.disable() # make problems with multi-processing

def worker_process_plan(plan:Plan):
    '''
    Function that actually does the process
    
    :param plan: plan to be processed and converted, any other informations are taken from above
    '''
    try:
        problem_filename_base = g_name_parser(plan.plan_name)
        problem_file = os.path.join(g_problem_path, f"{problem_filename_base}.pddl")
        
        if not os.path.exists(problem_file):
            logger.error(f"Problem file not found: {problem_file}")
            return

        with open(problem_file, 'r') as problem:
            problem_text = problem.read().lower()

        vfg_plan_instance:VfgPlan = g_VfgPlanClass(plan, g_domain_text, problem_text)
        viz_instance:Visualizer = g_VisualizerClass(
            vfg_plan_instance,
            g_format, 
            g_result_folder_name, 
            g_animation_profile_text
        )

        viz_instance.save_media()

    except Exception as e:
        logger.exception(f"Failed processing plan {g_name_parser(plan.plan_name)}: {e}")

class GenericConverter:
    def __init__(self, domain_path: str, problem_path: str, plan_path: Union[str, List[str]], animation_profile_path: str, format: str, save_path: str, visualizer_class: Type, vfg_plan_class: Type, n_jobs: int = 1, name_parser: Callable[[str], str] = None):
        '''
        :param domain_path: path of the pddl domain file
        :type domain_path: str
        :param problem_path: path of the folder containing the pddl problems
        :type problem_path: str
        :param plan_path: path, or list of paths, to the plan files
        :type plan_path: Union[str, List[str]]
        :param animation_profile_path: path to the pddl animation profile
        :type animation_profile_path: str
        :param format: format for the result
        :type format: str
        :param save_path: path for saving the results
        :type save_path: str
        :param visualizer_class: class of the Visualizer object
        :type visualizer_class: Type
        :param vfg_plan_class: class of the VfgPlan
        :type vfg_plan_class: Type
        :param n_jobs: cpu processors reserved for the task
        :type n_jobs: int, default 1
        :param name_parser: function to correctely parse the name of the problem
        :type name_parser: Callable[[str], str]
        '''
        
        with open(domain_path, 'r') as domain_file:
            self.domain_text = domain_file.read().lower()

        with open(animation_profile_path, "r") as profile:
            self.animation_profile_text = profile.read()

        self.problem_path = problem_path
        self.plan_path = plan_path
        self.format = format if format in ['mp4', 'png', 'gif'] else 'png'
        
        self.folder_name = os.path.join(save_path, self.format)
        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)

        self.visualizer_class = visualizer_class
        self.vfg_plan_class = vfg_plan_class
        self.name_parser = name_parser
        self.n_jobs = n_jobs if n_jobs is not None else 1

    def convert_plans(self):
        paths = [self.plan_path] if isinstance(self.plan_path, str) else self.plan_path
        
        # the same for the domain
        init_args = (
            self.domain_text,
            self.animation_profile_text,
            self.problem_path,
            self.folder_name,
            self.format,
            self.visualizer_class,
            self.vfg_plan_class,
            self.name_parser
        )

        for path in paths:
            try:
                if not os.path.exists(path):
                    logger.debug(f"Skipping non existent plan file: {path}")
                    continue
                    
                with open(path, "rb") as f:
                    plans_list = pickle.load(f)
                
                plan_file_name = os.path.basename(path)
                logger.info(f"Converting {len(plans_list)} plans from {plan_file_name} to {self.format} using {self.n_jobs} processes...")

                # multi process operation
                with logging_redirect_tqdm():
                    with Pool(processes=self.n_jobs, initializer=worker_initializer, initargs=init_args, maxtasksperchild=5) as pool:
                        list(
                            tqdm(
                                pool.imap_unordered(worker_process_plan, plans_list, chunksize=1), 
                                total=len(plans_list),
                                desc=f"Processing {plan_file_name}"
                            )
                        )
                    
                del plans_list
                gc.collect()

            except Exception as e:
                logger.exception(f"Error processing file {path}: {e}")

## functions to parse the problem name into the actual name
def blocksworld_problem_name_parser(plan_name: str) -> str:
    '''
    Function to correctely parse the plan name for BlocksWorld domain.
    
    :param plan_name: whole plan name
    :type plan_name: str
    :return: the correct problem name
    :rtype: str
    '''
    pattern = r'p\d+(?:_\d+)?'
    match = re.search(pattern, os.path.basename(plan_name))
    if match:
        full_match = match.group()
        return full_match.split('_')[0]
    return os.path.basename(plan_name).split('.')[0]

def logistics_problem_name_parser(plan_name: str)-> str:
    '''
    Function to correctely parse the plan name for Logistic domain.
    
    :param plan_name: whole plan name
    :type plan_name: str
    :return: the correct problem name
    :rtype: str
    '''
    return plan_name