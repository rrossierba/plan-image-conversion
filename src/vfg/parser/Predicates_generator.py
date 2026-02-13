#-----------------------------Authorship-----------------------------------------
#-- Authors  : Gang CHEN
#-- Group    : Planning Visualisation
#-- Date     : 13/August/2018
#-- Version  : 1.0
#--------------------------------------------------------------------------------
#-----------------------------Reviewer-------------------------------------------
#-- Authors  : Sharukh
#-- Group    : Planning Visualisation
#-- Date     : 23/August/2018
#-- Version  : 1.0
#--------------------------------------------------------------------------------
#-----------------------------Authorship-----------------------------------------
#-- Authors  : Sunmuyu Zhang
#-- Group    : Planning Visualisation
#-- Date     : 07/Septemeber/2018
#-- Version  : 2.0
#--------------------------------------------------------------------------------
#-----------------------------Reviewer-------------------------------------------
#-- Authors  : Sai
#-- Group    : Planning Visualisation
#-- Date     : 09/Septemeber/2018
#-- Version  : 2.0
#--------------------------------------------------------------------------------
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import Problem_parser
import re

def convert_predicate(predicate_string):
    BASE_OBJECT = {
        'name':'',
        'objectNames':[],
        }

    NO_OBJECTS = 'No objects'
    predicate = predicate_string.strip()
    predicate_elements = predicate.split(' ')
    predicate_name = predicate_elements[0]

    if predicate_name == predicate:
        predicate_args = NO_OBJECTS
    else:
        predicate_args = predicate_elements[1:]

    predicate_object = BASE_OBJECT.copy()
    predicate_object['name'] = predicate_name
    predicate_object['objectNames'] = predicate_args
    return predicate_object

def get_stages_from_pddl_plan(plan, problem_dic, problem_file, predicates_list, animation_profile=None):
    """
    The function is to get the list of steps for Step3 to use
    :param plan: solution file in pddl format
    :param problem_dic: problem dictionary contains the initial and goal stages
    :param problem_file: problem file name
    :param predicates_list: a list of predicates
    :param animation_profile: animation profile
    :return:  a list of steps containing information about all stages
    """
    
    # Initial stage
    stages = problem_dic[0]['init'].copy()
    objects = Problem_parser.get_object_list(problem_file)
    # finalstage = problem_dic[1]['goal'].copy()

    # Getting the list of actions from results returned from planning.domain api
    try:
        actionlist = plan['result']['plan']
    except KeyError:
        raise Exception("No plan has been returned")

    action_effect_list = get_action_effect_list(actionlist)

    # Final result structure
    content = {"stages": [], "objects": objects, "subgoals": []}
    # Adding initial stage
    content['stages'].append({
        "items": stages.copy(),
        "add": "",
        "remove": "",
        "stageName": "Initial Stage",
        "stageInfo": "No Step Information",
    })

    if animation_profile and animation_profile.get("cost_keyword") is not None:
        current_cost = 0
        content['stages'][0]["cost"] = current_cost
    else:
        current_cost = None

    for counter in range(len(actionlist)):
        add_predicate_list, remove_predicate_list = Problem_parser.get_separate_state_list(predicates_list, action_effect_list[counter])

        # 1. Find the difference between 2 steps
        for predicate in add_predicate_list:
            if predicate in stages:
                add_predicate_list.remove(predicate)
        for predicate in remove_predicate_list:
            if predicate not in stages:
                remove_predicate_list.remove(predicate)

        # Append the list to get the final result
        for add_predicate in add_predicate_list:
            stages.append(add_predicate)
        for remove_predicate in remove_predicate_list:
            stages.remove(remove_predicate)

        # 2.
        # Get the action name of this step from the plan
        action_name = actionlist[counter]['name']

        # 3.
        # Get the step information about the current step
        # Replacing \n with \r\n in order to display it correctly
        step_info_with_padding = actionlist[counter]['action'].replace("\n", "\r\n")
        step_info = step_info_with_padding[step_info_with_padding.index("(:action"):]

        if current_cost is not None:
            current_cost += get_action_cost(action_effect_list[counter], animation_profile["cost_keyword"])

        # 4.
        # Append everything to get the final output - content

        result = {"items": stages.copy(),
                  "add": add_predicate_list,
                  "remove": remove_predicate_list,
                  "stageName": action_name,
                  "stageInfo": step_info
                  }
        if current_cost is not None:
            result["cost"] = current_cost

        content['stages'].append(result)

    return content

def get_stages(plan, problem_dic, problem_file, animation_profile=None):
    """
    The function is to get the list of steps for Step3 to use
    :param plan: solution file
    :param problem_dic: problem dictionary contains the initial and goal stages
    :param problem_file: problem file name
    :param animation_profile: animation profile
    :return:  a list of steps containing information about all stages
    """

    # Initial stage
    stages = problem_dic[0]['init'].copy()
    objects = Problem_parser.get_object_list(problem_file)
    #finalstage = problem_dic[1]['goal'].copy()

    actionlist = plan.actions

    # Final result structure
    content = {"stages": [], "objects": objects, "subgoals": []}
    
    # Adding initial stage
    content['stages'].append({
        "items": stages.copy(),
        "add": "",
        "remove": "",
        "stageName": "Initial Stage"
    })

    if animation_profile and animation_profile.get("cost_keyword") is not None:
        current_cost = 0
        content['stages'][0]["cost"] = current_cost
    else:
        current_cost = None

    for action in actionlist:
        add_predicate_list = [convert_predicate(pred) for pred in action.positiveEffects]
        remove_predicate_list = [convert_predicate(pred) for pred in action.negativeEffects]

        # 1. Find the difference between 2 steps
        for predicate in add_predicate_list:
            if predicate in stages:
                add_predicate_list.remove(predicate)
        
        for predicate in remove_predicate_list:
            if predicate not in stages:
                remove_predicate_list.remove(predicate)

        for add_predicate in add_predicate_list:
            stages.append(add_predicate)
        for remove_predicate in remove_predicate_list:
            stages.remove(remove_predicate)

        result = {"items": stages.copy(),
                  "add": add_predicate_list,
                  "remove": remove_predicate_list,
                  "stageName": action.name.lower()
                  }
        
        if (animation_profile is not None) and (current_cost is not None):
            current_cost += get_action_cost(action, animation_profile["cost_keyword"])
            result["cost"] = current_cost

        content['stages'].append(result)

    return content


def get_action_effect_list(action_list):
    """The function will only keep the effect part of text for each action
        Args:
            action_list: an array of actions [{"action":"text"},{"action":"text"}.....]
        Returns:
            action_effect_list: a cleaned action list.
    """
    action_effect_list = []
    for action in action_list:
        effect_element = action['action']
        clearnedstr = (effect_element[effect_element.index("effect")
                                      + len("effect"):])
        action_effect_list.append(clearnedstr[:-1])
    return action_effect_list

def get_action_cost(action_effect, cost_keyword): # TO BE REFINED
    pattern = r"{}\s+(-?\d+(?:\.\d+)?)".format(cost_keyword)
    match = re.search(pattern, action_effect)
    if match:
        cost = float(match.group(1))
        return cost
    else:
        return 0
