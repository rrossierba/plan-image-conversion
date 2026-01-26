import pickle, os, sys, re

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from plan import Plan
from vfg_plan import BlocksworldVfgPlan, Visualizer, VfgPlan
from tqdm import tqdm
import pickle

def get_blocksworld_images_from_plan(plan:Plan, format:str, save_path:str):
    plan_name = re.search(r'p\d+', os.path.basename(plan.plan_name)).group()
    
    with open('files/blocksworld_files/plans/domain.pddl', 'r') as domain_file:
        domain_text = domain_file.read().lower()

    with open(f'files/blocksworld_files/plans/{plan_name}.pddl', 'r') as problem:
        problem_text = problem.read().lower()

    folder_name = f"{save_path}/{plan_name}_{format}"
    
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    vfg_plan = BlocksworldVfgPlan(plan, domain_text, problem_text)
    visualizer = Visualizer('files/ap.pddl')
    visualizer.save_media(vfg_plan, format=format, result_folder=folder_name)
    plan_description = str(plan)
    
    with open(f"{folder_name}/plan_description.txt", "w") as desc_file:
        desc_file.write(plan_description)

def convert_blocksworld_plans(plan_path, format, save_path):
    if plan_path.__class__ == str:
        plans_file_list = [pickle.load(open(plan_path, "rb"))]
        plans_file_name = [os.path.basename(plan_path)]
    elif plan_path.__class__ == list:
        plans_file_list = []
        plans_file_name = []
        for path in plan_path:
            plans_file_list.append(pickle.load(open(path, "rb")))
            plans_file_name.append(os.path.basename(path))

        
    for plans, plan_file_name in zip(plans_file_list, plans_file_name):
        print(f"Converting {len(plans)} plans from {plan_file_name} to images...")
        for plan in tqdm(plans):
            get_blocksworld_images_from_plan(plan, format=format, save_path=save_path)
        