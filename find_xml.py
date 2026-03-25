import xml.etree.ElementTree as ET

try:
    tree = ET.parse(r"d:\User\Ajeeth\Master Thesis\Voice controlled EMS\simulations\show_little_finger.osim")
    root = tree.getroot()
    print("Root tag:", root.tag)
    
    # Let's just find anything with FPL in it via string search just to be safe
    with open(r"d:\User\Ajeeth\Master Thesis\Voice controlled EMS\simulations\show_little_finger.osim", "r", encoding="utf-8") as f:
        data = f.read()
        print("FPL in file?", "FPL" in data)
        print("Schutte in file?", "Schutte" in data)
        print("Muscle in file?", "Muscle" in data)
        print("default_activation in file?", "default_activation" in data)

except Exception as e:
    print("Error:", e)
