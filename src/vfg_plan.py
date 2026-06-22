import json

from plan import Plan
from vfg.parser.Animation_parser import get_animation_profile
from vfg.solver.Solver import get_visualisation_dic
from vfg.adapter.visualiser_adapter.Transfer import generate_visualisation_file

from vfg.parser.Domain_parser import get_domain_json
from vfg.parser.Problem_parser import get_problem_dic
from vfg.parser.Predicates_generator import get_stages

from typing import Dict

class VfgPlan:
    def __init__(self, plan:Plan, domain_text:str, problem_text:str):
        '''
        :param plan: plan to be converted into a VfgPlan
        :type plan: Plan
        :param domain_text: string representing the domain
        :type domain_text: str
        :param problem_text: string representing the problem instance solved by plan
        :type problem_text: str
        '''
        self.plan:Plan = plan
        self.domain_text:str = domain_text
        self.problem_text:str = problem_text
        self.domain_dict:Dict = get_domain_json(self.domain_text)
        self.problem_dict:Dict = get_problem_dic(self.problem_text, self.domain_dict)
        self.stages:Dict = get_stages(self.plan, self.problem_dict, self.problem_text)
    
    def get_vfg(self, animation_profile_pddl):   
        animation_profile:Dict = json.loads(get_animation_profile(animation_profile_pddl, self.stages['objects']))
        visualisation_dic:Dict = get_visualisation_dic(self.stages, animation_profile, self.problem_dict)
        return generate_visualisation_file(visualisation_dic, self.stages['objects'], animation_profile)

class BlocksWorldVfgPlan(VfgPlan):
    '''
    BlocksWorldVfgPlan: VfgPlan subclass for blocksworld domain
    '''
    def __init__(self, plan:Plan, domain_text, problem_text):
        super().__init__(plan, domain_text, problem_text)
    
    def calculate_max_dimensions(self):
        '''
        Return the number of the objects in the problem, the maximum dimension if each block is on top of the other or if every block is on the table.
        '''
        return len(self.stages.get('objects'))
    
class LogisticsVfgPlan(VfgPlan):
    def __init__(self, plan: Plan, domain_text: str, problem_text: str):
        super().__init__(plan, domain_text, problem_text)

    def get_max_elements(self):
        max_at = 0
        max_in_city = 0

        for stage in self.stages['stages']:
            at_counts = {}
            in_city_counts = {}
            
            for item in stage['items']:
                name = item['name']
                objs = item['objectNames']
                
                if name == 'at' and len(objs) >= 2:
                    loc = objs[1]
                    at_counts[loc] = at_counts.get(loc, 0) + 1
                elif name == 'in-city' and len(objs) >= 2:
                    city = objs[1]
                    in_city_counts[city] = in_city_counts.get(city, 0) + 1
                    
            if at_counts:
                max_at = max(max_at, max(at_counts.values()))
            if in_city_counts:
                max_in_city = max(max_in_city, max(in_city_counts.values()))

        return max_at, max_in_city
    
    def get_object_counts(self):
        '''
        Count objects by type prefix for layout calculations.
        Returns a dict with counts of cities, locations, airports, trucks, airplanes, packages.
        '''
        objects = self.stages.get('objects', [])
        counts = {
            'cities': 0,
            'locations': 0, 
            'airports': 0,
            'trucks': 0,
            'airplanes': 0,
            'packages': 0,
            'total': len(objects)
        }
        for obj in objects:
            if obj.startswith('cit'):
                counts['cities'] += 1
            elif obj.startswith('pos'):
                counts['locations'] += 1
            elif obj.startswith('apt'):
                counts['airports'] += 1
            elif obj.startswith('tru'):
                counts['trucks'] += 1
            elif obj.startswith('apn'):
                counts['airplanes'] += 1
            elif obj.startswith('obj'):
                counts['packages'] += 1
        return counts