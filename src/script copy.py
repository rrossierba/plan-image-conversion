import pickle, json, time, zipfile, os, sys
from plan import Plan
from action import Action
from exporter import create_media
from vfg_plan import BlocksworldVfgPlan

# parser
from vfg.parser.Plan_generator import get_plan, get_plan_actions
from vfg.parser.Predicates_generator import get_stages
from vfg.parser.Domain_parser import get_domain_json
from vfg.parser.Problem_parser import get_problem_dic, get_object_list
from vfg.parser.Animation_parser import get_animation_profile

# solver
from vfg.solver.Solver import get_visualisation_dic

# transfer
from vfg.adapter.visualiser_adapter.Transfer import generate_visualisation_file

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

BLOCKSWORLD_DOMAIN_JSON = {'on': 2, 'on-table': 1, 'clear': 1, 'arm-empty': 0, 'holding': 1}

def load_all_plans():
    with (open("train_plans", "rb")) as openfile:
        try:
            plans = pickle.load(openfile)
            print(f"Loaded {len(plans)} plans")
            pickle.dump(plans[0:10], open("single_plan", "wb"))
        except EOFError:
            pass
            
def print_single_plan():
    plan = load_single_plan()
    print(plan.plan_name)
    print("Initial State:")
    for state in plan.initial_state:
        print(f" - {state}")
    print("Goals:")
    for goal in plan.goals:
        print(f" - {goal}")
    print("Actions:")
    for action in plan.actions:
        print(f" - {action.name} - {action.precondition} -> {action.positiveEffects} / {action.negativeEffects}")

def load_single_plan():
    with (open("plans/single_plan", "rb")) as openfile:
        plans = pickle.load(openfile)
        return plans[1]

BASE_OBJECT = {
    'name':'',
    'objectNames':[],
}

NO_OBJECTS = 'No objects'

BASE_STAGE = {
    'items':[],
    'add':[],
    'remove':[],
    'stageName':'',
}

def convert_predicate_to_stage_object(predicate_string, object_set=None):
    predicate = predicate_string.strip()
    predicate_elements = predicate.split(' ')
    predicate_name = predicate_elements[0]

    if predicate_name == predicate:
        predicate_args = NO_OBJECTS
    else:
        predicate_args = predicate_elements[1:]

    state_object = BASE_OBJECT.copy()
    state_object['name'] = predicate_name
    state_object['objectNames'] = predicate_args

    if object_set is not None:
        for obj in predicate_args:
            if obj != ' ' and predicate_args != NO_OBJECTS :
                object_set.add(obj)
    return state_object

def convert_plan_to_stages_json():
    plan = load_single_plan()
    
    # elements for the stages json
    plan_objects = set()
    stages = []

    # convert the initial state
    initial_state = BASE_STAGE.copy()
    initial_state['stageName'] = 'Initial Stage'
    initial_state['add'] = ''
    initial_state['remove'] = ''
    initial_state['items'] = [convert_predicate_to_stage_object(predicate, plan_objects) for predicate in plan.initial_state]

    current_state = set(plan.initial_state)

    stages.append(initial_state)
    # now convert the actions
    for action in plan.actions:
        new_stage = BASE_STAGE.copy()
        new_stage['stageName'] = f'({action.name.lower()})'

        # update the current state
        current_state = current_state - set(action.negativeEffects)
        current_state = current_state.union(set(action.positiveEffects))     
        
        # extract the items in the updated current state
        new_stage['items'] = [convert_predicate_to_stage_object(predicate) for predicate in current_state]

        # remove the negative effects and add the positive effects
        new_stage['remove'] = [convert_predicate_to_stage_object(neg_effect) for neg_effect in action.negativeEffects]
        new_stage['add']= [convert_predicate_to_stage_object(pos_effect) for pos_effect in action.positiveEffects]

        stages.append(new_stage)
    
    # final step
    stages_json = {
        'stages': stages,
        'objects': list(plan_objects)
    }

    # with (open('stages_from_plan.json', 'w')) as stages_file:
    #     json.dump(stages_json, stages_file, indent=4)
    
    return stages_json

def convert_plan_to_problem_json():
    plan = load_single_plan()
    init = [convert_predicate_to_stage_object(predicate) for predicate in plan.initial_state]
    goal = [convert_predicate_to_stage_object(predicate) for predicate in plan.goals]

    return [
        {'init': init},
        {'goal': goal,
         'goal-condition': ['and']}
    ]

def get_plan_planimation():

    claw_x = 500
    claw_y = 1000

    with (open("blocksworld_files/plans/domain.pddl", "r")) as domain_file:
        domain_pddl = domain_file.read()
    with (open("ap.pddl", "r")) as animation_profile_file:
        animation_profile_pddl = animation_profile_file.read()
        animation_profile_pddl = animation_profile_pddl.replace("CLAW_X", str(claw_x))
        animation_profile_pddl = animation_profile_pddl.replace("CLAW_Y", str(claw_y))

    start_time = time.time()

    # domain_json = BLOCKSWORLD_DOMAIN_JSON
    domain_json = get_domain_json(domain_pddl)
    # problem_dic = get_problem_dic(problem_pddl, domain_json)

    # print(problem_dic)
    
    # i need stages and animation profile for next steps
    # stages = get_stages(plan, problem_dic, problem_pddl, domain_json, {"cost_keyword": None}) # stages needs plan, problem_dic, problem_file, domain_json, and animation_profile (it can be a dictionary with the 'cost_keyword' key set to None)

    # with (open('stages_output.json', 'w')) as stages_output_file:
    #     json.dump(stages, stages_output_file, indent=4)

    # for s in stages['stages']:
    #     del s['stageName']
    #     del s['stageInfo']

    #
    problem_dic = convert_plan_to_problem_json()
    stages = convert_plan_to_stages_json()

    animation_profile = json.loads(get_animation_profile(animation_profile_pddl, domain_json)) # animation_profile needs animation_profile_file and domain_json

    # now we enter in the solver
    visualisation_dic = get_visualisation_dic(stages, animation_profile, problem_dic)
    visualisation_dic['subgoals'] = {}
    
    # now we are in the adapter
    object_list = stages['objects']
    vfg_json = generate_visualisation_file(visualisation_dic, object_list, animation_profile)
    
    # with the vfg we can create the media
    format = "png"
    result = create_media(vfg_json, format)

    stop_time = time.time()
    print(f"Execution time: {stop_time - start_time} seconds")

    if result:
        with zipfile.ZipFile(result, 'r') as zip_ref:
            zip_ref.extractall("result")

def get_images_from_plan():
    plan = load_single_plan()
    animation_profile_args = {
        'claw_x': 500,
        'claw_y': 1000,
        'animation_profile_path': 'pddl/ap.pddl'
    }

    vfg_json = BlocksworldVfgPlan(plan, animation_profile_args).get_vfg()
    
    format = "png"
    result = create_media(vfg_json, format)
    if result:
        with zipfile.ZipFile(result, 'r') as zip_ref:
            zip_ref.extractall("result")
    

if __name__ == "__main__":
    start_time = time.time()
    get_images_from_plan()
    stop_time = time.time()
    print(f"Execution time: {stop_time - start_time} seconds")