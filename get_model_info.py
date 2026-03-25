
import opensim as osim
import os

def list_model_details(model_path):
    print(f"Loading Model: {model_path}")
    
    if not os.path.exists(model_path):
        print("ERROR: Model file not found!")
        return

    try:
        model = osim.Model(model_path)
        model.initSystem()
        
        muscles = model.getMuscles()
        joints = model.getCoordinateSet()
        
        print("\n=== MUSCLES (" + str(muscles.getSize()) + ") ===")
        muscle_names = [muscles.get(i).getName() for i in range(muscles.getSize())]
        print(muscle_names)
        
        print("\n=== JOINTS (" + str(joints.getSize()) + ") ===")
        joint_names = [joints.get(i).getName() for i in range(joints.getSize())]
        print(joint_names)
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    # Path to your Wrist Model
    model_path = r"C:\OpenSim 4.5\Resources\Models\WristModel\wristmod2prueb2.osim"
    list_model_details(model_path)
