# DataCopilot

DataCopilot is a FastAPI-based battery data analysis platform designed for battery research, data exploration, and battery performance evaluation.

Current capabilities include:

- Excel dataset upload
- Correlation analysis
- Scatter and line plots
- Cycle summary and cycle comparison
- Capacity retention analysis
- Capacity-Voltage (Q-V) curves
- dQ/dV analysis
- Cross-cycle dQ/dV comparison

---

# Features

## Raw Data Analysis

- View dataset columns
- Correlation analysis
- Top correlations
- Scatter plots
- Line plots

## Cycle Analysis

- Cycle list
- Cycle summary
- Cycle step analysis
- Cycle comparison

## Battery Analytics

- Capacity retention
- Capacity retention curve
- Capacity-Voltage (Q-V) curve
- dQ/dV curve
- Cycle-to-cycle dQ/dV comparison

---

# Environment Setup

Due to system security restrictions, installing Python packages directly into the system environment may not be allowed.

It is recommended to use a Python virtual environment.

## 1. Create a Virtual Environment

```bash
python3 -m venv .venv
```

## 2. Activate the Virtual Environment

```bash
source .venv/bin/activate
```

## 3. Install Required Packages

```bash
pip install -r requirements.txt
```

---

# Running the Application

## Development Mode

```bash
python -m uvicorn app:app --reload
```

## Run with Custom Host and Port

```bash
python -m uvicorn app:app \
    --host 0.0.0.0 \
    --port 8888
```

Example:

```bash
http://<server-ip>:8888
```

---

# Virtual Environment Structure

```text
(.venv)
├── python
├── pip
└── uvicorn
```

---

# Project Structure

```text
DataCopilot
│
├── app.py
│
├── api
│   ├── system.py
│   ├── upload.py
│   ├── raw_data.py
│   └── cycle.py
│
├── core
│   └── datastore.py
│
├── tools
│   ├── plotting.py
│   ├── correlation.py
│   └── statistics.py
│
├── data
│
├── out
│
├── .venv
│
└── README.md
```

---

# API Documentation

After starting the application, open Swagger UI:

```text
http://localhost:8000/docs
```

or

```text
http://<server-ip>:8888/docs
```

Swagger UI provides interactive testing for all available APIs.

---

# Output Files

Generated plots are automatically saved under:

```text
out/
```

Example:

```text
out/
├── scatter_plot_*.png
├── cycle_plot_*.png
├── capacity_retention_*.png
├── capacity_voltage_*.png
├── dqdv_cycle_*.png
└── dqdv_comparison_*.png
```

---

# Example Workflow

1. Upload a battery test Excel file

```text
POST /upload
```

2. View available columns

```text
GET /raw-columns
```

3. Analyze correlations

```text
GET /correlation
```

4. View cycle summary

```text
GET /cycle-summary?cycle=108
```

5. Plot capacity retention

```text
GET /capacity-retention-curve
```

6. Plot dQ/dV

```text
GET /dqdv-curve?cycle=108
```

7. Compare cycles

```text
GET /cycle-comparison-dqdv?cycle1=1&cycle2=108
```

---

## Future Work

- Automated battery report generation
- Peak detection and battery aging analysis
- LLM-powered natural language querying
- Multi-dataset comparison
- Report export (PDF/PowerPoint)

---

# Technology Stack

- Python
- FastAPI
- Uvicorn
- Pandas
- NumPy
- SciPy
- Matplotlib
- OpenPyXL

---

# License

For research and educational purposes.