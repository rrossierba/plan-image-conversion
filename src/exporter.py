import sys
import os

import zipfile
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
from matplotlib.animation import FFMpegWriter
from matplotlib.animation import PillowWriter

from PIL import Image
from io import BytesIO
import base64
import numpy as np
import tempfile

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# A few constants
_STATES_PER_SECOND = 1.5
QUALITY_SETTINGS = {
    "low": {"interp_frames": 2},
    "medium": {"interp_frames": 6},
    "high": {"interp_frames": 10}
}

def export_media(vfg_json, format, parameters):
    if parameters==None:
        quality = 'medium'
    else:
        quality = parameters.get("quality")
        if quality not in ["low", "medium", "high"]:
            quality = "medium"

    if format in ["mp4", "png"]:
        try:
            return create_media(vfg_json, format, quality)
        finally:
            plt.close('all')
    elif format == "webm":
        return "error"
    return "error"

def apply_tint(image, color):
    r, g, b, a = np.rollaxis(image, axis=-1)
    r = np.clip(np.uint8(r * color[0]), 0, 255)
    g = np.clip(np.uint8(g * color[1]), 0, 255)
    b = np.clip(np.uint8(b * color[2]), 0, 255)
    tinted_image = np.stack([r, g, b, a], axis=-1)
    return tinted_image

class LoopingPillowWriter(PillowWriter):
    def finish(self):
        self._frames[0].save(
            self._outfile, save_all=True, append_images=self._frames[1:],
            duration=int(1000 / self.fps), loop=0)

def create_media(vfg_json, format, quality='medium'):
    chosen_quality = QUALITY_SETTINGS.get(quality, QUALITY_SETTINGS["high"])
    num_interpolation_frames = chosen_quality["interp_frames"]

    startStep = 0
    stopStep  = len(vfg_json.get('visualStages')) if vfg_json.get('visualStages') else 1
    visual_stages = vfg_json['visualStages'][startStep:stopStep+1]

    all_sprites = [s for stage in vfg_json['visualStages'] for s in stage['visualSprites']]
    max_x = max(s['x'] + s['width'] for s in all_sprites) if all_sprites else 100
    max_y = max(s['y'] + s['height'] for s in all_sprites) if all_sprites else 100
    del all_sprites # clear cache

    last_positions = {}
    image_table = {}
    tint_cache = {}

    image_keys = vfg_json.get("imageTable", {}).get("m_keys", [])
    image_values = vfg_json.get("imageTable", {}).get("m_values", [])
    for key, base64_str in zip(image_keys, image_values):
        try:
            image_data = base64.b64decode(base64_str)
            image = Image.open(BytesIO(image_data)).convert("RGBA")
            image_table[key] = np.array(image)
        except:
            continue

    try:
        if format in ["mp4", "gif"]:
            fig, ax = plt.subplots()
            plt.close(fig) 
            fig = plt.figure() 
            ax = fig.add_subplot(111)
            
            ax.axis('equal')
            ax.axis('off')

            def update(frame):
                ax.clear()
                ax.set_aspect('equal', adjustable='box')
                ax.axis('off')
                ax.set_xlim([0, max_x])
                ax.set_ylim([0, max_y])

                active_frames = len(visual_stages) * num_interpolation_frames
                if frame >= active_frames:
                    stage = visual_stages[-1]
                    interpolation_alpha = 1
                else:
                    interpolation_alpha = frame % num_interpolation_frames / (num_interpolation_frames - 1)
                    stage_idx = frame // num_interpolation_frames
                    stage = visual_stages[stage_idx]

                process_sprites(stage, last_positions, interpolation_alpha, image_table, tint_cache, ax)

            total_frames = len(visual_stages) * num_interpolation_frames + int(1 * num_interpolation_frames)
            fps = int(num_interpolation_frames * _STATES_PER_SECOND)

            with tempfile.NamedTemporaryFile(delete=False, suffix="."+format) as tmpfile:
                tmpname = tmpfile.name

            try:
                if format == "mp4":
                    ani = FuncAnimation(fig, update, frames=total_frames, repeat=False, save_count=1)
                    writer = FFMpegWriter(fps=fps, bitrate=1800)
                    ani.save(tmpname, writer=writer)
                elif format == "gif":
                    ani = FuncAnimation(fig, update, frames=total_frames, repeat=True, save_count=1)
                    writer = LoopingPillowWriter(fps=fps)
                    ani.save(tmpname, writer=writer)
                
                output = BytesIO()
                with open(tmpname, "rb") as f:
                    output.write(f.read())
                output.seek(0)
                return output
            finally:
                plt.close('all')
                if os.path.exists(tmpname):
                    os.remove(tmpname)

        elif format == "png":
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                fig = plt.figure()
                ax = fig.add_subplot(111)

                for idx, stage in enumerate(visual_stages, start=startStep):
                    ax.clear()
                    ax.set_aspect('equal', adjustable='box')
                    ax.axis('off')
                    ax.set_xlim([0, max_x])
                    ax.set_ylim([0, max_y])
                    
                    process_sprites(stage, last_positions, None, image_table, tint_cache, ax)

                    img_buf = io.BytesIO()
                    fig.savefig(img_buf, format="png", bbox_inches='tight')
                    zipf.writestr(f"state_{idx}.png", img_buf.getvalue())
                    
                    img_buf.close() 

                plt.close(fig)

            zip_buffer.seek(0)
            return zip_buffer
            
    finally:
        plt.close('all')
        tint_cache.clear()
        image_table.clear()
        last_positions.clear()

def process_sprites(stage, last_positions, interpolation_alpha, image_table, tint_cache, ax):
    current_sprite_names = set()
    
    for sprite in stage['visualSprites']:
        x, y, w, h = sprite['x'], sprite['y'], sprite['width'], sprite['height']
        color = (sprite['color']['r'], sprite['color']['g'], sprite['color']['b'], sprite['color']['a'])
        name = sprite['name']
        
        current_sprite_names.add(name)
        
        if name in last_positions and interpolation_alpha is not None:
            x_last, y_last = last_positions[name]
            x = np.interp(interpolation_alpha, [0, 1], [x_last, x])
            y = np.interp(interpolation_alpha, [0, 1], [y_last, y])
        
        prefab_image = sprite.get('prefabimage', None)
        
        if prefab_image and prefab_image in image_table:
            cache_key = (prefab_image, tuple(color))
            
            if cache_key not in tint_cache:
                image = image_table[prefab_image]
                tinted_image = apply_tint(image, color)
                tint_cache[cache_key] = tinted_image
            
            ax.imshow(tint_cache[cache_key], extent=[x, x+w, y, y+h], origin='upper', interpolation='bilinear')
        else:
            rect = patches.Rectangle(
                (x, y), w, h, linewidth=0, edgecolor='none', facecolor=color
            )
            ax.add_patch(rect)
        
        last_positions[name] = (x, y)
        
        if sprite.get('showname', False):
            ax.text(
                x + w/2, y + h/2, name.upper(), 
                ha='center', va='center',
                color='white' if sum(color[:3]) < 1.5 else 'black'
            )
        
        if sprite.get('showlabel', False):
            label = str(sprite.get('label'))
            labelcolor = sprite.get('labelcolor', 'black')
            labelcolor = (labelcolor['r'], labelcolor['g'], labelcolor['b'], labelcolor['a'])
            ax.text(
                x + w/2, y + h/2, label.upper(), 
                ha='center', va='center',
                color=labelcolor
            )

    if interpolation_alpha is None:
        sprites_to_remove = set(last_positions.keys()) - current_sprite_names
        for sprite_name in sprites_to_remove:
            del last_positions[sprite_name]