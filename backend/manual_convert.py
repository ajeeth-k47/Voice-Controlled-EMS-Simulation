import os
import sys

# Ensure the converter modules can be found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from osimConverters.convertOsim2Gltf import convertOsim2Gltf
from osimViewerOptions import osimViewerOptions

# 1. EXACT PATH to your generated .osim file
# You can change this to point to any other .osim file you have generated
# model_file = r'C:\OpenSim 4.5\Resources\Models\WristModel\wristmod2prueb2.osim'

model_file = "../simulations/peace_sign.osim"

# 2. Add the motion file (.sto) if you have an animation, otherwise leave the list empty []
motion_files = [] 
# For example: motion_files = [r'C:\path\to\your_simulation.sto']

# 3. Output path
frontend_public = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'public')
output_gltf = os.path.join(frontend_public, 'test_model.gltf')

model_dir = os.path.dirname(model_file)
os.chdir(model_dir) 

# Configure options
options = osimViewerOptions()
options.setShowMuscles(True)

try:
    print(f"Loading {model_file}...")
    gltf = convertOsim2Gltf(model_file, model_dir, motion_files, options)
    gltf.save(output_gltf)
    print(f"SUCCESS! Saved GLTF to: {output_gltf}")
except Exception as e:
    import traceback
    traceback.print_exc()
