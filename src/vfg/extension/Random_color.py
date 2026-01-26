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
    # Genera valori tra 0.6 e 1.0 per assicurare che sia chiaro e non scuro
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