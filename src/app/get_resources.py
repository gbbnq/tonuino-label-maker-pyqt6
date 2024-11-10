import os
import sys
import json
from PIL import Image

def resource_path(relative_path:str):
    """
    Get the absolute path to the resource, works for dev and for PyInstaller
    
    Args:
        relative_path (str): Path to resource file
    """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

try:
    json_path = resource_path('..\\resources\\templates.json')
    with open(json_path, 'r') as file:
        template_data = json.load(file)
except:
    json_path = resource_path('resources\\templates.json')
    with open(json_path, 'r') as file:
        template_data = json.load(file)
        
try:
    espuino_logo_path = resource_path('..\\resources\\espuino_logo.png')
    espuino_logo = Image.open(espuino_logo_path)
except:
    espuino_logo_path = resource_path('resources\\espuino_logo.png')
    espuino_logo = Image.open(espuino_logo_path)
    
try:
    tonuino_logo_path = resource_path('..\\resources\\tonuino_logo.png')
    tonuino_logo = Image.open(tonuino_logo_path)
except:
    tonuino_logo_path = resource_path('resources\\tonuino_logo.png')
    tonuino_logo = Image.open(tonuino_logo_path)