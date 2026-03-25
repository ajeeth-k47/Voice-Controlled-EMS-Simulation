# LLM Hand Movement App (Master Thesis)

## Startup Instructions

### 1. Backend (FastAPI + Simulation)
The simulation and hardware mock run on the backend.
**Command:**
```bash
conda activate opensim-env
python -m uvicorn backend.main:app --reload --port 8000
```

### 2. Frontend (React)
The 3D Interface and Voice Control.
**Command:**
```bash
cd frontend
npm run dev
```

### 3. Evaluation — generated motions to Excel
After generating `*_coords.mot` files under `simulations/`, export them to `Evaluation/Generated/`:

```bash
python backend/mot_to_excel.py --input simulations --output_dir Evaluation/Generated
```

Requires: `pandas`, `openpyxl` (see `requirements.txt`).

### 4. Evaluation report
Fill `Evaluation/Baseline/` and `Evaluation/Generated/` (see `Evaluation/README.md`), then:

```bash
python Evaluation/generate_evaluation_report.py
```

Output: `Evaluation/report/` (CSV + Markdown). Logic lives only in `Evaluation/generate_evaluation_report.py`.

**Metrics (angles):** **`Evaluation/README.md`**.

### Joint angles (LLM → OpenSim)
- **`backend/joint_angle_postprocess.py`**: if the LLM omits DIP joints but PIP is flexed, **DIP is set from PIP** (capped at 90°) before `simulate_gesture` runs, so `*_coords.mot` is not missing fingertip flex.
- **`backend/llm_service.py`**: prompt + JSON example now list **DIP** and thumb-related coordinates (`TCP2M_flex`, `TCP2M2_flex`, etc.) so the model outputs complete chains where possible.

