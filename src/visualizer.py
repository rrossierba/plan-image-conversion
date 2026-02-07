import matplotlib
from vfg_plan import VfgPlan, BlocksworldVfgPlan
import zipfile, os
from exporter import create_media

class Visualizer:
    def __init__(self, vfg_plan:VfgPlan, format:str, result_folder:str, animation_profile_text:str, animation_profile_params:dict={}):
        '''
        :param vfg_plan: VfgPlan Object
        :param format: format to save the results, 'png' or 'mp4'
        :param result_folder: folder path where to save results
        :param animation_profile_text: animation profile in a string form
        :param animation_profile_params: dictionary for the parameters to adjust the animation profile
        '''
        self.vfg_plan = vfg_plan
        self.format = format
        self.result_folder = result_folder
        self.animation_profile_text = animation_profile_text
        self.animation_profile_params = animation_profile_params

    def save_media(self):
        '''
        Function that use the parameter of the Visualizer to save the media in the right folder with the right format.
        '''
        animation_profile = self.adjust_animation_profile()
        vfg_json = self.vfg_plan.get_vfg(animation_profile)
        folder_name = f"{self.result_folder}/{self.get_plan_name()}"

        result = create_media(vfg_json, self.format, quality='medium')
        if self.format == 'png':
            if result:
                folder_name = f'{folder_name}/'
                if not os.path.exists(folder_name):
                    os.makedirs(folder_name)
                with zipfile.ZipFile(result, 'r') as zip_ref:
                    zip_ref.extractall(folder_name)
        elif self.format == 'mp4':
            if result:
                with open(f"{folder_name}_animation.mp4", "wb") as f:
                    f.write(result.getbuffer())

    def adjust_animation_profile(self):
        return self.animation_profile_text
    
    def get_plan_name(self):
        return self.vfg_plan.plan.plan_name.split('/')[-1]

class BlocksWorldVisualizer(Visualizer):
    def __init__(self, blocksworld_vfg_plan:BlocksworldVfgPlan, format, result_folder, animation_profile_text, plan_name, figsize=15, dpi=100):
        '''
        :param blocksworld_vfg_plan: BlocksworldVfgPlan object
        :param format: as Visualizer
        :param result_folder: as Visualizer
        :param animation_profile_text: as Visualizer
        :param plan_name: plan name to save the results in the correct way
        :param figsize: figure size for the matplotlib library
        :param dpi: dpi for the matplotlib library
        '''
        
        animation_profile_params = {
            'max_dimensions':blocksworld_vfg_plan.calculate_max_dimensions()
        }
        self.plan_name = plan_name
        self.figsize = figsize
        self.dpi = dpi
        super().__init__(blocksworld_vfg_plan, format, result_folder, animation_profile_text, animation_profile_params)
    
    def adjust_animation_profile(self):
        '''
        Function that calculates the position of some BlocksWorld elements dinamically
        '''

        # calculate the dimension in an adaptive way
        max_dimensions = self.animation_profile_params.get('max_dimensions', (10,10))
        max_width, max_height = max_dimensions
        max_dim = max(max_width, max_height)
        
        block_space_ratio = 20 if (max_dim > 10) else 10
        
        block_size = (self.figsize*self.dpi)//max_dim
        block_space_between = block_size // block_space_ratio
        claw_width = block_size
        claw_height = claw_width // 2
        
        claw_x = ((block_size + block_space_between) * (max_dim) )//2
        claw_y = int(block_size * (max_height + 1))

        ceiling_y = claw_y + claw_height
        
        holding_effect = block_size - claw_height//2
        board_height = 4
        
        # apply the dimensions to the animation profile
        new_animation_profile = self.animation_profile_text.format_map({
            'CLAW_X': str(claw_x),
            'CLAW_Y': str(claw_y),
            'BLOCK_SIZE': str(block_size),
            'SPACE_BETWEEN_BLOCKS': str(block_space_between),
            'HOLDING_EFFECT': str(holding_effect),
            'CLAW_WIDTH': str(claw_width),
            'CLAW_HEIGHT': str(claw_height),
            'BOARD_HEIGHT': str(board_height),
            'CEILING_Y': str(ceiling_y),
        })

        # update rcparams of matplotlib
        matplotlib.rcParams.update({
            'figure.figsize': (self.figsize, self.figsize),
            'font.size': block_size // 3,
            'figure.subplot.left': 0.01,
            'figure.subplot.right': 0.99,
            'figure.subplot.bottom': 0.01,
            'figure.subplot.top': 0.99
        })

        return new_animation_profile

    def get_plan_name(self):
        return self.plan_name