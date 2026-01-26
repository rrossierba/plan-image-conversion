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
    '''
    Classe specifica per la rappresentazione del piano nel dominio Blocksworld.
    Eredita dalla classe VfgPlan e implementa metodi specifici per calcolare le dimensioni massime della configurazione dei blocchi durante l'esecuzione del piano.

    Attributes:
        plan (Plan): L'oggetto piano che rappresenta la sequenza di azioni.
        domain_text (str): Il testo del dominio PDDL.
        problem_text (str): Il testo del problema PDDL.
    Methods:
        calculate_max_dimensions(): Calcola la larghezza e l'altezza massima della configurazione dei blocchi durante l'esecuzione del piano.
    '''
    
    def __init__(self, plan:Plan, domain_text, problem_text):
        super().__init__(plan, domain_text, problem_text)
    
    def calculate_max_dimensions(self):
        on_table = set() # planimation keep a state, where each block on the table is stored, but never removed, hence a new block on the table is always add to the end (left) of this state
        max_height = 0

        for stage in self.stages['stages']:
            items = stage['items']
            
            block_dic = {
                'table':set(),
            }

            for item in items:
                if item['name']== 'on-table':
                    block_dic['table'].add(item['objectNames'][0])
                if item['name'] == 'on':
                    above_block = item['objectNames'][0]
                    below_block = item['objectNames'][1]
                    block_dic[below_block] = above_block
                if item['name'] == 'clear':
                    block_dic[item['objectNames'][0]] = 'clear'

            on_table = on_table.union(block_dic['table'])
            
            # calculate max height
            for table_block in block_dic['table']:
                current_height = 0
                current_block = table_block
                while current_block != 'clear':
                    current_block = block_dic[current_block]
                    current_height += 1
                
                if current_height > max_height:
                    max_height = current_height
        
        max_width = len(on_table)
        return max_width, max_height

class Visualizer:
    def __init__(self, animation_profile_path, figsize=15, dpi=100):
        self.animation_profile_path = animation_profile_path
        self.figsize = figsize
        self.dpi = dpi

    def save_media(self, vfg_plan, format='png', result_folder='result'):
        ap = self.adjust_animation_profile(vfg_plan.calculate_max_dimensions())
        vfg_json = vfg_plan.get_vfg(ap)
        result = create_media(vfg_json, format, quality='medium')

        if format == 'png':
            if result:
                with zipfile.ZipFile(result, 'r') as zip_ref:
                    zip_ref.extractall(result_folder)
        elif format == 'mp4':
            if result:
                with open(f"{result_folder}/animation.mp4", "wb") as f:
                    f.write(result.getbuffer())

    def adjust_animation_profile(self, max_dimensions=(10,10)):
        max_width, max_height = max_dimensions
        max_dim = max(max_width, max_height)
        
        block_space_ratio = 20 if (max_dim > 10) else 10
        
        block_size = (self.figsize*self.dpi)//max_dim
        block_space_between = block_size // block_space_ratio
        claw_width = block_size
        claw_height = claw_width // 2
        
        claw_x = ((block_size + block_space_between) * (max_dim) )//2
        claw_y = int(block_size * (max_height + 1))
        
        holding_effect = block_size - claw_height//2
        board_height = 4
        
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
            'figure.subplot.left': 0.01,
            'figure.subplot.right': 0.99,
            'figure.subplot.bottom': 0.01,
            'figure.subplot.top': 0.99
        })

        return animation_profile_pddl    