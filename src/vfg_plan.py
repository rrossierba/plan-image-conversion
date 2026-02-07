import json

from plan import Plan
from vfg.parser.Animation_parser import get_animation_profile
from vfg.solver.Solver import get_visualisation_dic
from vfg.adapter.visualiser_adapter.Transfer import generate_visualisation_file

from vfg.parser.Domain_parser import get_domain_json
from vfg.parser.Problem_parser import get_problem_dic
from vfg.parser.Predicates_generator import get_stages

class VfgPlan:
    def __init__(self, plan:Plan, domain_text, problem_text):
        '''
        Docstring per __init__
        
        :param self: Descrizione
        :param plan: Descrizione
        :type plan: Plan
        :param domain_text: Descrizione
        :param problem_text: Descrizione
        '''
        self.plan = plan
        self.domain_text = domain_text
        self.problem_text = problem_text
        self.domain_dict = get_domain_json(self.domain_text)
        self.problem_dict = get_problem_dic(self.problem_text, self.domain_dict)
        self.stages = get_stages(self.plan, self.problem_dict, self.problem_text)
    
    def get_vfg(self, animation_profile_pddl):   
        animation_profile = json.loads(get_animation_profile(animation_profile_pddl, self.stages['objects']))
        visualisation_dic = get_visualisation_dic(self.stages, animation_profile, self.problem_dict)
        return generate_visualisation_file(visualisation_dic, self.stages['objects'], animation_profile)

class BlocksworldVfgPlan(VfgPlan):
    def __init__(self, plan:Plan, domain_text, problem_text):
        super().__init__(plan, domain_text, problem_text)
    
    def calculate_max_dimensions(self):
        '''
        Docstring per calculate_max_dimensions
        
        :param self: Descrizione
        '''
        on_table = set()
        max_height = 0
        
        for stage in self.stages['stages']:
            block_relations = {}
            current_table_blocks = set()
            
            for item in stage['items']:
                name = item['name']
                obj = item['objectNames'][0]
                
                if name == 'on-table':
                    current_table_blocks.add(obj)
                    on_table.add(obj)
                elif name == 'on':
                    block_relations[item['objectNames'][1]] = obj
                elif name == 'clear':
                    block_relations[obj] = None
            
            for table_block in current_table_blocks:
                height = 1
                current = table_block
                
                while current in block_relations and block_relations[current] is not None:
                    current = block_relations[current]
                    height += 1

                max_height = max(max_height, height)

        return len(on_table), max_height