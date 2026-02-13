import pickle, os, sys, re

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from multiprocessing import Pool, cpu_count
from plan import Plan
from vfg_plan import *
from visualizer import *
from tqdm import tqdm
import pickle

class Converter:
    def __init__(self, domain_path:str, problem_path:str, plan_path:str, animation_profile_path:str, format:str, save_path:str, n_jobs:int=None):
        """
        :param domain_path: percorso del file di dominio del problema
        :type domain_path: str
        :param problem_path: percorso della cartella contenente i file pddl dei problemi
        :type problem_path: str
        :param plan_path: percorso del file pkl contenente i piani
        :type plan_path: str
        :param animation_profile_path: percorso del file animation profile in pddl
        :type animation_profile_path: str
        :param format: formato del risultato: mp4 o png
        :type format: str
        :param save_path: percorso della cartella in cui salvare i risultati
        :type save_path: str
        """

        with open(domain_path, 'r') as domain_file:
            self.domain_text = domain_file.read().lower()

        self.plan_path = plan_path
        
        with (open(animation_profile_path, "r")) as animation_profile_file:
            self.animation_profile_text = animation_profile_file.read()

        self.problem_path = problem_path
        self.format = format if format in ['mp4', 'png'] else None
        self.folder_name = f"{save_path}/{format}"
        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)

        self.n_jobs = n_jobs if n_jobs is not None else cpu_count()

    def get_media_from_plan(self, plan:Plan):
        '''
        Function that takes a plan and convert it into media.
        Needs to be implemented by subclasses.
        '''
        raise NotImplementedError

    def convert_plans(self):
        '''
        Function to convert the plans to the 
        '''

        if self.plan_path.__class__ == str:
            plans_file_list = [pickle.load(open(self.plan_path, "rb"))]
            plans_file_name = [os.path.basename(self.plan_path)]
        elif self.plan_path.__class__ == list:
            plans_file_list = []
            plans_file_name = []
            for path in self.plan_path:
                plans_file_list.append(pickle.load(open(path, "rb")))
                plans_file_name.append(os.path.basename(path))

        # for plans, plan_file_name in zip(plans_file_list, plans_file_name):
        #     print(f"Converting {len(plans)} plans from {plan_file_name} to {self.format}...")
        #     for plan in tqdm(plans):
        #         self.get_media_from_plan(plan)

        for plans, plan_file_name in zip(plans_file_list, plans_file_name):
            print(f"Converting {len(plans)} plans from {plan_file_name} to {self.format} using {self.n_jobs} processes...")
            
            with Pool(processes=self.n_jobs) as pool:
                with tqdm(total=len(plans), desc=f"Processing {plan_file_name}") as pbar:
                    for _ in pool.imap_unordered(self.get_media_from_plan, plans, chunksize=1):
                        pbar.update(1)
    
class BlocksWorldConverter(Converter):
    def get_media_from_plan(self, plan:Plan):
        '''
        Function that takes a plan and convert it into a blocksworld image.

        :param plan: Plan object to be converted
        :type plan: Plan
        '''
        pattern = r'p\d+(?:_\d+)?'
        plan_name = re.search(pattern, os.path.basename(plan.plan_name)).group()
        
        with open(f'{self.problem_path}/{plan_name.split('_')[0]}.pddl', 'r') as problem:
            problem_text = problem.read().lower()

        BlocksWorldVisualizer(
            blocksworld_vfg_plan=BlocksworldVfgPlan(plan, self.domain_text, problem_text), 
            format=self.format, 
            result_folder=self.folder_name, 
            plan_name=plan_name,
            animation_profile_text=self.animation_profile_text
        ).save_media()

class LogisticsConverter(Converter):
    def get_media_from_plan(self, plan):
        pass