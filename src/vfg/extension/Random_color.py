"""This module is designed to help with getting a randomly selected color"""
# -----------------------------Authorship-----------------------------------------
# -- Authors  : Sai
# -- Group    : Planning Visualisation
# -- Date     : 13/August/2018
# -- Version  : 1.0
# --------------------------------------------------------------------------------
# -----------------------------Reviewer-------------------------------------------
# -- Authors  : Yi Ding
# -- Group    : Planning Visualisation
# -- Date     : 17/October/2018
# -- Version  : 1.0
# --------------------------------------------------------------------------------
import random

# Lista di colori pastello curata (Chiari, Luminosi, Morbidi)
random_colorList = [
    # --- Tonalità Calde (Rosa, Pesca, Giallo) ---
    {'r': 1.0, 'g': 0.8, 'b': 0.81, 'a': 1.0},  # Rosa Confetto
    {'r': 1.0, 'g': 0.89, 'b': 0.77, 'a': 1.0}, # Pesca Chiaro
    {'r': 1.0, 'g': 0.99, 'b': 0.82, 'a': 1.0}, # Giallo Crema
    {'r': 1.0, 'g': 0.71, 'b': 0.76, 'a': 1.0}, # Rosa Fenicottero Light
    {'r': 0.98, 'g': 0.85, 'b': 0.77, 'a': 1.0}, # Albicocca
    
    # --- Tonalità Fredde (Blu, Azzurro, Lavanda) ---
    {'r': 0.69, 'g': 0.88, 'b': 0.9, 'a': 1.0},  # Azzurro Ghiaccio
    {'r': 0.85, 'g': 0.85, 'b': 1.0, 'a': 1.0},  # Lavanda Chiaro
    {'r': 0.68, 'g': 0.85, 'b': 0.9, 'a': 1.0},  # Blu Polvere
    {'r': 0.8, 'g': 0.94, 'b': 1.0, 'a': 1.0},   # Ciano Chiarissimo
    {'r': 0.73, 'g': 0.69, 'b': 0.91, 'a': 1.0}, # Lilla Pastello

    # --- Tonalità Naturali (Verde, Menta, Acqua) ---
    {'r': 0.8, 'g': 1.0, 'b': 0.8, 'a': 1.0},    # Verde Menta
    {'r': 0.6, 'g': 0.98, 'b': 0.6, 'a': 1.0},   # Verde Pastello
    {'r': 0.74, 'g': 0.93, 'b': 0.85, 'a': 1.0}, # Verde Acqua Tenue
    {'r': 0.88, 'g': 1.0, 'b': 0.95, 'a': 1.0},  # Verde Schiuma
    
    # --- Neutri (Grigio caldo, Beige) ---
    {'r': 0.94, 'g': 0.94, 'b': 0.9, 'a': 1.0},  # Beige Avorio
    {'r': 0.9, 'g': 0.9, 'b': 0.92, 'a': 1.0},   # Grigio Perla
]

def get_dynamic_pastel_color():
    """
    Genera un colore pastello casuale calcolando valori alti.
    """
    r = random.uniform(0.6, 1.0)
    g = random.uniform(0.6, 1.0)
    b = random.uniform(0.6, 1.0)
    
    return {'r': r, 'g': g, 'b': b, 'a': 1.0}

# This function will provide a randomly selected color for Initialise to use.
def get_random_color():
    """
    This function randomly selects a color from the predefined list of colors
    :return: a random color dict
    """
    #return random.choice(random_colorList)
    return get_dynamic_pastel_color()

def get_white():
    return {'r': 1.0, 'g': 1.0, 'b': 1.0, 'a': 1.0}

def get_deterministic_color(object_name):
    # random.seed(object_name)
    # r = random.uniform(0.65, 1.0)
    # g = random.uniform(0.65, 1.0)
    # b = random.uniform(0.65, 1.0)
    # return {'r': r, 'g': g, 'b': b, 'a': 1.0}

    alphabet_colors_mapping = {
        "A": {"r": 1.0, "g": 0.70, "b": 0.73, "a": 1.0},    # Rosa Pastello
        "B": {"r": 1.0, "g": 0.87, "b": 0.73, "a": 1.0},    # Pesca
        "C": {"r": 1.0, "g": 1.0, "b": 0.73, "a": 1.0},     # Giallo Crema
        "D": {"r": 0.73, "g": 1.0, "b": 0.79, "a": 1.0},    # Verde Menta
        "E": {"r": 0.73, "g": 0.88, "b": 1.0, "a": 1.0},    # Celeste
        "F": {"r": 0.87, "g": 0.73, "b": 1.0, "a": 1.0},    # Lavanda
        "G": {"r": 1.0, "g": 0.73, "b": 0.87, "a": 1.0},    # Rosa Orchidea
        "H": {"r": 0.73, "g": 1.0, "b": 0.94, "a": 1.0},    # Turchese Chiaro
        "I": {"r": 1.0, "g": 0.85, "b": 0.76, "a": 1.0},    # Albicocca
        "J": {"r": 0.88, "g": 0.95, "b": 0.69, "a": 1.0},   # Lime Tenue
        "K": {"r": 0.70, "g": 0.72, "b": 0.97, "a": 1.0},   # Blu Periwinkle
        "L": {"r": 0.99, "g": 0.80, "b": 0.90, "a": 1.0},   # Rosa Confetto
        "M": {"r": 0.81, "g": 0.98, "b": 1.0, "a": 1.0},    # Acqua
        "N": {"r": 1.0, "g": 0.93, "b": 0.87, "a": 1.0},    # Crema Scuro
        "O": {"r": 0.86, "g": 0.86, "b": 0.86, "a": 1.0},   # Grigio Perla
        "P": {"r": 1.0, "g": 0.78, "b": 0.59, "a": 1.0},    # Arancio Tenue
        "Q": {"r": 0.63, "g": 0.91, "b": 0.90, "a": 1.0},   # Tiffany
        "R": {"r": 0.71, "g": 0.97, "b": 0.78, "a": 1.0},   # Smeraldo Chiaro
        "S": {"r": 0.98, "g": 0.63, "b": 0.69, "a": 1.0},   # Salmone
        "T": {"r": 0.64, "g": 0.82, "b": 1.0, "a": 1.0},    # Sky Blue
        "U": {"r": 1.0, "g": 0.69, "b": 0.80, "a": 1.0},    # Bubblegum
        "V": {"r": 0.74, "g": 0.70, "b": 1.0, "a": 1.0},    # Violetto
        "W": {"r": 0.79, "g": 1.0, "b": 0.75, "a": 1.0},    # Green Glow
        "X": {"r": 0.99, "g": 1.0, "b": 0.71, "a": 1.0},    # Canary
        "Y": {"r": 1.0, "g": 0.78, "b": 1.0, "a": 1.0},     # Mauve
        "Z": {"r": 0.61, "g": 0.96, "b": 1.0, "a": 1.0}     # Cyan Elettrico Tenue
    }

    return alphabet_colors_mapping.get(object_name.upper(), None)

def get_deterministic_color_logistics(object_name):
    color_map = {'obj00': {'a': 1.0, 'b': 0.59, 'g': 0.98, 'r': 0.98},
 'obj11': {'a': 1.0, 'b': 0.43, 'g': 0.66, 'r': 0.93},
 'obj12': {'a': 1.0, 'b': 0.56, 'g': 0.94, 'r': 0.97},
 'obj13': {'a': 1.0, 'b': 0.41, 'g': 0.6, 'r': 0.92},
 'obj21': {'a': 1.0, 'b': 0.54, 'g': 0.9, 'r': 0.96},
 'obj22': {'a': 1.0, 'b': 0.39, 'g': 0.55, 'r': 0.91},
 'obj23': {'a': 1.0, 'b': 0.52, 'g': 0.85, 'r': 0.96},
 'obj33': {'a': 1.0, 'b': 0.37, 'g': 0.49, 'r': 0.9},
 'obj44': {'a': 1.0, 'b': 0.5, 'g': 0.81, 'r': 0.95},
 'obj55': {'a': 1.0, 'b': 0.35, 'g': 0.43, 'r': 0.9},
 'obj66': {'a': 1.0, 'b': 0.47, 'g': 0.76, 'r': 0.94},
 'obj77': {'a': 1.0, 'b': 0.33, 'g': 0.37, 'r': 0.89},
 'obj88': {'a': 1.0, 'b': 0.45, 'g': 0.71, 'r': 0.93},
 'obj99': {'a': 1.0, 'b': 0.31, 'g': 0.31, 'r': 0.88}}
    
    return color_map[object_name]