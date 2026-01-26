import json, zipfile
import matplotlib
from plan import Plan
from vfg.parser.Animation_parser import get_animation_profile
from vfg.solver.Solver import get_visualisation_dic
from vfg.adapter.visualiser_adapter.Transfer import generate_visualisation_file
from exporter import create_media

from vfg.parser.Domain_parser import get_domain_json
from vfg.parser.Problem_parser import get_problem_dic
from vfg.parser.Predicates_generator import get_stages

class VfgPlan:
    def __init__(self, plan:Plan, domain_text, problem_text):
        self.plan = plan
        self.domain_text = domain_text
        self.problem_text = problem_text
        self.domain_dict = get_domain_json(self.domain_text)
        self.problem_dict = get_problem_dic(self.problem_text, self.domain_dict)
        self.stages = get_stages(self.plan, self.problem_dict, self.problem_text)
    
    def get_vfg(self, animation_profile_pddl):   
        animation_profile = json.loads(get_animation_profile(animation_profile_pddl, self.stages['objects']))
        visualisation_dic = get_visualisation_dic(self.stages, animation_profile, self.problem_dict)
        visualisation_dic['subgoals'] = []
        return generate_visualisation_file(visualisation_dic, self.stages['objects'], animation_profile)

class BlocksworldVfgPlan(VfgPlan):
    def __init__(self, plan:Plan, domain_text, problem_text):
        super().__init__(plan, domain_text, problem_text)
    
    def calculate_max_dimensions(self):
        max_width = 0

        for stage in self.stages['stages']:
            items = stage['items']
            ontable_count = 0
            for item in items:
                if item['name'] == 'on-table':
                    ontable_count += 1
            
            if ontable_count > max_width:
                max_width = ontable_count
        
        return max_width
    
class Visualizer:
    def __init__(self, animation_profile_path, figsize=15, dpi=100):
        self.animation_profile_path = animation_profile_path
        self.figsize = figsize
        self.dpi = dpi

    def save_media(self, vfg_plan, format='png', result_folder='result'):
        ap = self.adjust_animation_profile(vfg_plan.calculate_max_dimensions())
        vfg_json = vfg_plan.get_vfg(ap)
        result = create_media(vfg_json, format)

        if format == 'png':
            if result:
                with zipfile.ZipFile(result, 'r') as zip_ref:
                    zip_ref.extractall(result_folder)

    def adjust_animation_profile(self, max_width=7):
        claw_x = claw_y = (self.figsize+2)*self.dpi
        block_size = self.figsize*self.dpi//(max_width + 2)
        block_space_between = 40
        claw_width = block_size
        claw_height = claw_width // 2
        holding_effect = block_size - claw_height // 2
        board_height = 5
        
        with (open(self.animation_profile_path, "r")) as animation_profile_file:
            animation_profile_pddl = animation_profile_file.read()
            animation_profile_pddl = animation_profile_pddl.replace("CLAW_X", str(claw_x))
            animation_profile_pddl = animation_profile_pddl.replace("CLAW_Y", str(claw_y))
            animation_profile_pddl = animation_profile_pddl.replace("BLOCK_SIZE", str(block_size))
            animation_profile_pddl = animation_profile_pddl.replace("SPACE_BETWEEN_BLOCKS", str(block_space_between))
            animation_profile_pddl = animation_profile_pddl.replace("HOLDING_EFFECT", str(holding_effect))
            animation_profile_pddl = animation_profile_pddl.replace("CLAW_WIDTH", str(claw_width))
            animation_profile_pddl = animation_profile_pddl.replace("CLAW_HEIGHT", str(claw_height))
            animation_profile_pddl = animation_profile_pddl.replace("BOARD_HEIGHT", str(board_height))

        matplotlib.rcParams.update({
            'figure.figsize': (self.figsize, self.figsize),
            'font.size': block_size // 3,
        })

        return animation_profile_pddl    