import subprocess
subprocess.run([
    r'C:\Users\write\.conda\envs\opensim-env\python.exe', 
    'backend/open_sim_runner.py', 
    '--gesture', 'test_motion', 
    '--amp', '15', 
    '--freq', '40', 
    '--width', '300', 
    '--muscles', '[]'
])
