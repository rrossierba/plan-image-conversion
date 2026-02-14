import os, sys, pickle
sys.path.append(os.path.dirname('src/'))
from action import Action
from plan import Plan

def extract_subset_plan(plan_file:str, output_file:str, initial_index:int=0, final_index:int=None):
    '''
    Utility function to extract a sublist of plans from a bigger plan list.
    
    :param plan_file: path to the plan list pkl file
    :type plan_file: str
    :param output_file: path for the pkl output
    :type output_file: str
    :param initial_index: initial index (included) for extracting plans sublist, default=0
    :type initial_index: int
    :param final_index: final index (excluded) for extracting plans sublist, default=None, if set to None it will be automatically set as the lenght of the original plan
    :type final_index: int
    '''
    if final_index and initial_index>final_index:
        raise ValueError('Final index must be smaller than initial index')

    with (open(plan_file, "rb")) as openfile:
        try:
            print('Loading plans')
            plans = pickle.load(openfile)
            print(f"Loaded {len(plans)} plans")
            
            if (final_index is None) or (final_index>len(plans)):
                final_index = len(plans)

            to_save = plans[initial_index:final_index]
            print(f"Extracting {len(to_save)} plans to {output_file}")
            pickle.dump(to_save, open(output_file, "wb"))
        except EOFError:
            print('End of file')


if __name__=='__main__':
    extract_subset_plan(
        '',
        ''
    )