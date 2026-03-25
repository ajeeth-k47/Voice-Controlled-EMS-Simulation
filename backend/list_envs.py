
import sys

print("Checking Gym vs Gymnasium...", flush=True)

try:
    import gymnasium
    import myosuite
    print(f"Gymnasium Version: {gymnasium.__version__}", flush=True)
    print("Listing MyoSuite Environments (via Gymnasium):", flush=True)
    for env_id in gymnasium.envs.registry.keys():
        if "myo" in env_id.lower():
            print(f"  [GYMNASIUM] {env_id}", flush=True)
except ImportError:
    print("Gymnasium not installed.", flush=True)

try:
    import gym
    import myosuite
    print(f"Gym Version: {gym.__version__}", flush=True)
    print("Listing MyoSuite Environments (via Gym):", flush=True)
    env_dict = gym.envs.registry.all() if hasattr(gym.envs.registry, 'all') else gym.envs.registry.keys()
    
    for env in env_dict:
        env_id = env.id if hasattr(env, 'id') else env
        if "myo" in str(env_id).lower():
            print(f"  [GYM] {env_id}", flush=True)
except ImportError:
    print("Gym not installed.", flush=True)
