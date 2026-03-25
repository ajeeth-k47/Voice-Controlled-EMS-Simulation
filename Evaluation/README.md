# Evaluation (baseline vs generated)

## Folders

| Folder | Contents |
|--------|----------|
| **`Baseline/`** | Excel (`.xlsx`) from OpenSim baseline motions, e.g. `I.xlsx` … `TR.xlsx` |
| **`Generated/`** | Excel from app motions: `simulations/*_coords.mot` → `backend/mot_to_excel.py` |
| **`report/`** | Output of angle evaluation (created automatically) |

## Baseline `.mot` → muscle activation `.sto` (step before activation evaluation)

Coordinate `.mot` files do **not** contain muscle activations. To get **activation time series** (0–1 per muscle) from the same baseline motions, run **Static Optimization** in OpenSim.

Default baseline motions (wrist model):

**`C:\OpenSim 4.5\Resources\Models\WristModel\Motionfiles`**

Script: **`Evaluation/motionfiles_mot_to_sto.py`** — for each `*.mot`, writes **`<same_stem>.sto`** in that folder (activation columns from SO). Intermediate SO outputs use `%TEMP%\opensim_so_motionfiles\`.

```bash
conda activate opensim-env
python Evaluation/motionfiles_mot_to_sto.py
```

| Flag | Meaning |
|------|--------|
| `--motion-dir` | Folder of `.mot` files (default: path above) |
| `--model` | `.osim` path (else `.env` `OPENSIM_MODEL_PATH` or wrist default) |
| `--external-loads` | Optional external loads XML |
| `--dry-run` | List inputs and target `.sto` paths only |
| `--only TM` | Run **one** motion (e.g. `TM.mot` only) for debugging |
| `-v` / `--verbose` | Print setup XML path; on failure, list any `.sto` files OpenSim wrote |

**Checklist if conversion “does not happen”**

1. **Conda env:** `import opensim` must work (`conda activate opensim-env`).
2. **End of log:** `Done: N ok, M failed` — if `M > 0`, read the `FAIL` lines above it.
3. **Scratch folder:** `%TEMP%\opensim_so_motionfiles\<name>\` — after a run you should see `*activation*.sto` there. The script copies the activation file to `Motionfiles\<name>.sto`.
4. **GUI fallback:** Open `...\AnalyzeTool_setup.xml` in the **OpenSim GUI** → run SO. If the GUI works but Python does not, compare errors.

*(Activation vs generated-app comparison / reports are not in this repo yet — add when you are ready for that evaluation step.)*

---

## Run the angle report

From the **project root**:

```bash
python Evaluation/generate_evaluation_report.py
```

**Outputs** (under `Evaluation/report/`):

- **`evaluation_summary.csv`** — one row per movement (pair of files).
- **`evaluation_details.csv`** — one row per **joint coordinate** that was compared.
- **`evaluation_report.md`** — short summary table + overall averages.

**Optional:** add `Evaluation/motion_pairs.csv` with columns `label`, `baseline_filename`, `generated_filename`.  
If that file is missing, the script uses the **built-in 15 movements** map (baseline `I.xlsx` ↔ generated `index_finger_flexion_coords.xlsx`, etc.).

---

## What is compared?

1. **Which columns:** only flexion-style coordinates: names ending in `_flex`, plus wrist **`flexion`**. The `time` column is ignored for metrics.
2. **Peak value:** for each of those columns, the **maximum angle (in degrees)** over the whole motion is taken — that is the **peak joint angle** for baseline and for generated.
3. **Which joints enter the score:** “**active**” coordinates are those where the **baseline** peak is **greater than** `--active-threshold-deg` (default **5°**). If none pass, the **three** largest baseline peaks are used instead.
4. **Timing is not used:** we do **not** compare *when* the peak happens, only the **peak magnitude**.

---

## Metrics (full names and how they are calculated)

Notation for one movement and one joint coordinate:

- **Baseline peak (degrees)** = maximum baseline angle for that coordinate.  
- **Generated peak (degrees)** = maximum generated angle for that coordinate.  
- **Absolute peak error (degrees)** = |generated peak − baseline peak|.

### Per joint (in `evaluation_details.csv`)

**Relative peak error (percent)** for that joint:

\[
\text{relative peak error (\%)} = 100 \times \frac{\text{absolute peak error (degrees)}}{\max(\text{baseline peak (degrees)},\, 1°)}
\]

The **1°** floor avoids dividing by a baseline peak that is almost zero.

### Per movement (in `evaluation_summary.csv`)

Let \(N\) = number of **active** joints for that movement.

**1. Mean absolute error of peak angles (degrees)** (`mae_peak_deg`)

\[
\text{MAE}_{\text{peak}} = \frac{1}{N} \sum \text{absolute peak error (degrees)}
\]

**2. Root mean square error of peak angles (degrees)** (`rmse_peak_deg`)

\[
\text{RMSE}_{\text{peak}} = \sqrt{\frac{1}{N} \sum \bigl(\text{absolute peak error (degrees)}\bigr)^2}
\]

**3. Mean relative peak error (percent)** (`mean_relative_peak_error_pct`)

\[
\text{mean relative peak error (\%)} = \frac{1}{N} \sum \text{relative peak error (\%)}
\]

**4. Peak similarity (percent)** (`peak_similarity_pct`)

\[
\text{peak similarity (\%)} = \text{clip}\bigl(100 - \text{mean relative peak error (\%)},\, 0,\, 100\bigr)
\]

Higher **peak similarity** means generated peaks are closer to baseline peaks **on average** (for those active joints). It is **not** a measure of full motion shape or timing.

### Overall section in `evaluation_report.md`

The markdown report also prints the **mean** of `mae_peak_deg`, `rmse_peak_deg`, and `peak_similarity_pct` **across all movements** that succeeded.

---

## Worked example (numbers)

Assume **one movement**, **three** active joints, baseline peaks and generated peaks as below.

| Coordinate | Baseline peak (°) | Generated peak (°) | Absolute peak error (°) | Denominator max(base, 1°) | Relative peak error (%) |
|------------|-------------------|---------------------|---------------------------|---------------------------|-------------------------|
| MCP2_flex  | 90                | 90                  | 0                         | 90                        | 100×0/90 = **0**        |
| PIP_flex   | 90                | 60                  | 30                        | 90                        | 100×30/90 ≈ **33.33**   |
| DIP_flex   | 90                | 0                   | 90                        | 90                        | 100×90/90 = **100**     |

- **Mean absolute error of peak angles** = (0 + 30 + 90) / 3 = **40°**  
- **Root mean square error of peak angles** = √[(0² + 30² + 90²) / 3] = √[(0 + 900 + 8100) / 3] ≈ **54.77°**  
- **Mean relative peak error** = (0 + 33.33 + 100) / 3 ≈ **44.44%**  
- **Peak similarity** = clip(100 − 44.44, 0, 100) ≈ **55.56%**

Your real tables have more joints and different numbers; the **details** CSV shows the same logic row by row.

---

## Export Excel before evaluating

```bash
python backend/mot_to_excel.py --input simulations --output_dir Evaluation/Generated
python backend/mot_to_excel.py --input "C:\OpenSim 4.5\Resources\Models\WristModel\Motionfiles" --output_dir Evaluation/Baseline
```

Requires `pandas` and `openpyxl` (see project `requirements.txt`).
