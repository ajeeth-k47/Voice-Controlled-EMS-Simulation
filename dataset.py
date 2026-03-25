import scipy.io
import numpy as np
import pandas as pd
import os

# ── CHANGE THIS to your actual dataset folder path ────────────────────
DATASET_PATH = r"D:\User\Ajeeth\Master Thesis\dataset"
# ─────────────────────────────────────────────────────────────────────

# ALL movements in E2 (basic finger + wrist movements)
E2_MOVEMENTS = {
    1:  "thumb_flexion_extension",
    2:  "thumb_abduction_adduction",
    3:  "index_flexion_extension",
    4:  "index_abduction_adduction",
    5:  "middle_flexion_extension",
    6:  "middle_abduction_adduction",
    7:  "ring_flexion_extension",
    8:  "ring_abduction_adduction",
    9:  "little_flexion_extension",
    10: "little_abduction_adduction",
    11: "wrist_flexion_extension",
    12: "wrist_radial_ulnar_deviation",
    13: "wrist_pronation_supination",
    14: "index_middle_extension",     # ← peace sign
    15: "ring_little_flexion",
    16: "all_fingers_abduction",
    17: "thumb_opposing_little",
    18: "pointing_index",
    19: "adduction_extended_fingers",
    20: "hand_open_close",
}

# ALL movements in E3 (grasping movements)
E3_MOVEMENTS = {
    1:  "large_diameter_grasp",       # ← closest to fist
    2:  "small_diameter_grasp",
    3:  "fixed_hook_grasp",
    4:  "index_finger_extension_grasp",
    5:  "medium_wrap",
    6:  "ring_grasp",
    7:  "prismatic_four_finger_grasp",
    8:  "stick_grasp",
    9:  "writing_tripod_grasp",
    10: "power_disk_grasp",
    11: "power_sphere_grasp",
    12: "three_finger_sphere_grasp",
    13: "precision_disk_grasp",
    14: "prismatic_pinch",
    15: "tip_pinch",
    16: "lateral_pinch",
    17: "palmar_pinch",
    18: "tripod_grasp",
    19: "parallel_extension",
    20: "adduction_grip",
}

def extract_avg_angles(dataset_path, exercise, movements_dict):
    # dictionary to collect per-subject averages
    all_subject_avgs = {name: [] for name in movements_dict.values()}
    angle_names = None

    for subj_num in range(1, 78):  # all 77 subjects
        folder = os.path.join(dataset_path, f"s_{subj_num}_angles")

        if not os.path.exists(folder):
            print(f"  Folder not found for subject {subj_num}, skipping")
            continue

        # find the correct .mat file for this exercise
        file = None
        for f in os.listdir(folder):
            if f"_E{exercise}_" in f and f.endswith(".mat"):
                file = os.path.join(folder, f)
                break

        if file is None:
            print(f"  Subject {subj_num} E{exercise}: file not found, skipping")
            continue

        try:
            data = scipy.io.loadmat(file)
        except Exception as e:
            print(f"  Could not load {file}: {e}")
            continue

        angles   = data['angles']            # shape: (N_timepoints, 22)
        stimulus = data['stimulus'].flatten() # shape: (N_timepoints,)
        # debug prints
        print(f"  angles shape:   {angles.shape}")
        print(f"  stimulus shape: {stimulus.shape}")

        min_len  = min(len(angles), len(stimulus))
        angles   = angles[:min_len]
        stimulus = stimulus[:min_len]

        # confirm after trim
        print(f"  after trim - angles: {angles.shape}, stimulus: {stimulus.shape}")


        # get angle column names once
        if angle_names is None:
            try:
                angle_names = [
                    str(data['order_of_angles'][0][i][0])
                    for i in range(22)
                ]
            except:
                angle_names = [f"angle_{i}" for i in range(22)]

        # extract average angles per movement for this subject
        for stim_num, mov_name in movements_dict.items():
            rows = angles[stimulus == stim_num]
            if len(rows) == 0:
                continue
            avg = np.mean(rows, axis=0)
            all_subject_avgs[mov_name].append(avg)

        if subj_num % 10 == 0:
            print(f"  Processed {subj_num}/77 subjects...")

    # average across all subjects
    results = {}
    for mov_name, subject_avgs in all_subject_avgs.items():
        if len(subject_avgs) > 0:
            results[mov_name] = np.mean(subject_avgs, axis=0)
        else:
            print(f"  WARNING: no data found for {mov_name}")

    return results, angle_names


print("=" * 50)
print("Processing Exercise 2 — basic finger movements")
print("=" * 50)
e2_results, angle_names = extract_avg_angles(DATASET_PATH, 2, E2_MOVEMENTS)

print("\n" + "=" * 50)
print("Processing Exercise 3 — grasping movements")
print("=" * 50)
e3_results, _ = extract_avg_angles(DATASET_PATH, 3, E3_MOVEMENTS)

# combine both exercises into one table
all_results = {**e2_results, **e3_results}

# build dataframe: rows = movements, columns = 22 joint angles
df = pd.DataFrame(all_results, index=angle_names).T
df.index.name = "movement"
df = df.round(2)

# save to CSV
output_path = os.path.join(DATASET_PATH, "ground_truth_angles_ALL.csv")
df.to_csv(output_path)

print(f"\n✓ Done! Saved to: {output_path}")
print(f"  Shape: {df.shape[0]} movements × {df.shape[1]} joint angles")
print("\nPreview (first 5 movements):")
print(df.head().to_string())
