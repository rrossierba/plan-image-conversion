from plan import Plan
from action import Action   
import pickle

def extract_subset_plan(plan_file, number_of_plans):
    output_file = "plans/subset_plans_last"

    with (open(plan_file, "rb")) as openfile:
        try:
            plans = pickle.load(openfile)
            print(f"Loaded {len(plans)} plans")
            to_save = plans[-number_of_plans:]
            print(f"Extracting {len(to_save)} plans to {output_file}")
            pickle.dump(to_save, open(output_file, "wb"))
        except EOFError:
            pass