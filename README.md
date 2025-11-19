# Nutritional Insights App

Interactive dashboard and analysis for dietary recipes, powered by a Flask backend API and a simple web UI.

## Overview

This project has been updated to include a Flask backend that serves nutritional data from the CSV file instead of hardcoding it in the frontend.

- **Web UI** (`project2ui.html`):
  - Bar chart: Average Protein/Carbs/Fat by diet type (loaded from API)
  - Pie chart: Recipe distribution per diet type (loaded from API)
  - Scatter plot: Top protein recipes vs carbs (loaded from API)
  - Filters (search + dropdown) and paginated table (3 rows/page)
  - Real-time API interaction buttons with live data
- **Backend API** (`backend/app.py`): Flask REST API that reads from CSV and provides endpoints
- **Data Source** (`All_Diets.csv`): CSV file containing nutritional information for recipes

## Project Structure

```
Project2/
├─ backend/
│  ├─ app.py              # Flask API server
│  ├─ requirements.txt    # Python dependencies
│  └─ README.md          # Backend documentation
├─ All_Diets.csv         # Data source
├─ project2ui.html        # Frontend dashboard
├─ start-backend.ps1     # Script to start the backend
└─ README.md (this file)
```

## Prerequisites (Windows)

- Python 3.8+ (available via the Windows launcher `py`)
- pip (comes with Python)

Check versions:

```powershell
py --version
py -m pip --version
```

## Quick Start

### Option 1: Using the PowerShell Script (Recommended)

Simply run the startup script from the Project2 directory:

```powershell
.\start-backend.ps1
```

This will automatically:
1. Check Python installation
2. Install required dependencies
3. Start the Flask backend server on `http://localhost:5000`

### Option 2: Manual Setup

#### 1) Install Backend Dependencies

```powershell
cd backend
py -m pip install -r requirements.txt
```

#### 2) Start the Backend Server

```powershell
py app.py
```

You should see:
```
Starting Nutritional Insights API...
CSV Path: <path-to-csv>
 * Running on http://0.0.0.0:5000
```

#### 3) Open the Web UI

- Open `project2ui.html` in your browser
- The dashboard will automatically connect to the backend and load data from the CSV
- All charts, filters, and API buttons will work with real-time data

## Dev Mode (.env) and One-Command Start

You can configure host/port and CSV path via a `.env` file in the project root.

1) Copy example and adjust as needed:

```powershell
Copy-Item .env.example .env
# then edit .env
```

Supported variables:

- `FLASK_ENV` or `FLASK_DEBUG=1`
- `HOST` (default `127.0.0.1`)
- `PORT` (default `5000`)
- `CSV_PATH` (default `All_Diets.csv`)

2) Start everything and open the UI with one command:

```powershell
./dev.ps1
```

`dev.ps1` will:
- Load `.env`
- Start the backend if not already running
- Wait until `/api/health` returns 200
- Open `project2ui.html` in your default browser

## Verify Locally (PowerShell)

After starting the backend, you can verify endpoints quickly:

```powershell
# Health check
Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/health" -UseBasicParsing |
  Select-Object StatusCode

# Nutrition summary (show totals only)
(Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/nutrition/summary" -UseBasicParsing).Content |
  ConvertFrom-Json | Select-Object status,total_records,diet_types

# Top protein recipes (first 5)
(Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/recipes/top-protein?limit=5" -UseBasicParsing).Content |
  ConvertFrom-Json | Select-Object status,count

# Recipe statistics
(Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/recipes" -UseBasicParsing).Content |
  ConvertFrom-Json | Select-Object status,@{n='total_recipes';e={$_.statistics.total_recipes}}

# Clusters
(Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/clusters" -UseBasicParsing).Content |
  ConvertFrom-Json | Select-Object status,clusters_identified
```

Open the UI directly from PowerShell:
py -m http.server 5500
# Then open http://localhost:5500/project2ui.html in your browser
```

## Data currently shown in the UI (synced from CSV)

Diet types and averages used by the dashboard:

- Dash: Protein 69.282275, Carbs 160.535754, Fat 101.150562, Recipes 1745
- Keto: Protein 101.266508, Carbs 57.970575, Fat 153.116356, Recipes 1512
- Mediterranean: Protein 101.112316, Carbs 152.905545, Fat 101.416138, Recipes 1753
- Paleo: Protein 88.674765, Carbs 129.552127, Fat 135.669027, Recipes 1274
- Vegan: Protein 56.157030, Carbs 254.004192, Fat 103.299678, Recipes 1522

These values are sourced from `Project1Files/All_Diets.csv` and match the latest run output printed by `data_analysis.py`.

## Troubleshooting
## Troubleshooting Section Summary

Here's a concise summary for your README:

---

### **Troubleshooting**

#### **Issue 1: `ModuleNotFoundError: No module named 'pandas'` (or numpy, seaborn, matplotlib)**

**Symptoms:**
```
ERROR: Unknown compiler(s): [['icl'], ['cl'], ['cc'], ['gcc']...]
× pip subprocess to install build dependencies did not run successfully.
```

**Cause:** Using Python 3.15 (or other very new Python versions) where pre-built wheels for pandas/numpy are not yet available. Pip attempts to build from source but fails due to missing C compiler.

**Solution:**
- Use Python 3.11 or 3.12 instead:
  ```bash
  py -3.12 -m pip install pandas seaborn matplotlib
  ```
- Download Python 3.12 from [python.org](https://www.python.org/downloads/) if not installed

---

#### **Issue 2: Script runs but can't find installed packages**

**Symptoms:**
```
ModuleNotFoundError: No module named 'pandas'
```
(Even after successful installation)

**Cause:** Packages installed in Python 3.12, but script running with a different Python version (e.g., 3.15).

**Solution:**
- Run script with the same Python version where packages were installed:
  ```bash
  py -3.12 Project1Files\data_analysis.py --csv Project1Files\All_Diets.csv --no-show
  ```
- Or set Python 3.12 as default by creating `C:\Users\[username]\AppData\Local\py.ini`:
  ```ini
  [defaults]
  python=3.12
  ```

---

**Recommendation:** Use Python 3.11 or 3.12 for data science projects as they have stable, pre-built packages available.

Recommendation: Use Python 3.11 or 3.12 for data science projects as they have stable, pre-built packages available.

- "Python was not found": use the Windows launcher `py` instead of `python3`.
- Missing packages (e.g., `ModuleNotFoundError: No module named 'pandas'`):

```powershell
Start-Process .\project2ui.html
```

## API Endpoints

The backend provides the following REST API endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/nutrition/summary` | GET | Aggregated nutrition data by diet type |
| `/api/recipes/top-protein?limit=5` | GET | Top protein-rich recipes |
| `/api/recipes?diet_type=keto` | GET | Recipe statistics (with optional diet filter) |
| `/api/clusters` | GET | Diet type cluster analysis |
| `/api/nutrition/all?page=1&per_page=50` | GET | Complete dataset (paginated) |

## Features

### Backend (Flask API)
- ✅ Reads data directly from CSV file
- ✅ RESTful API endpoints
- ✅ CORS enabled for frontend access
- ✅ Automatic data aggregation and calculations
- ✅ Pagination support for large datasets
- ✅ Real-time data processing from CSV

### Frontend (HTML Dashboard)
- ✅ Dynamic data loading from backend API
- ✅ Real-time chart updates
- ✅ Interactive filters and search
- ✅ API response timing display
- ✅ Error handling with user feedback
- ✅ Responsive design with Tailwind CSS

## Architecture

```
┌─────────────────┐
│  Web Browser    │
│ (project2ui.html)│
└────────┬────────┘
         │ HTTP Requests
         │ (fetch API)
         ▼
┌─────────────────┐
│  Flask API      │
│  (backend/app.py)│
└────────┬────────┘
         │ Reads CSV
         ▼
┌─────────────────┐
│  All_Diets.csv  │
│  (root directory)│
└─────────────────┘
```

### Backend Issues
- **"Python was not found"**: Use the Windows launcher `py` instead of `python3`
- **Backend won't start**: Ensure all dependencies are installed with `py -m pip install -r backend/requirements.txt`
- **Port 5000 already in use**: Stop other services using port 5000 or change the port in `backend/app.py`
- **CSV not found**: Verify `All_Diets.csv` exists in the Project2 root directory

### Frontend Issues
- **Charts not loading**: Ensure backend is running on `http://localhost:5000`
- **CORS errors**: Backend has CORS enabled; check browser console for specific errors
- **Data not displaying**: Check that `All_Diets.csv` exists and has the required columns

### Missing Packages
```powershell
py -m pip install flask flask-cors pandas numpy
```

## Technologies Used

- **Backend**: Python 3, Flask, Pandas, NumPy
- **Frontend**: HTML5, Tailwind CSS, Chart.js
- **Data**: CSV (All_Diets.csv - 7,806 records)

## Development

### To modify the API:
1. Edit `backend/app.py`
2. Restart the server
3. Frontend will automatically use the updated endpoints

### To modify the frontend:
1. Edit `project2ui.html`
2. Refresh the browser

## Architecture

```
┌─────────────────┐
│  Web Browser    │
│ (project2ui.html)│
└────────┬────────┘
         │ HTTP Requests
         │ (fetch API)
         ▼
┌─────────────────┐
│  Flask API      │
│  (backend/app.py)│
└────────┬────────┘
         │ Reads CSV
         ▼
┌─────────────────┐
│  All_Diets.csv  │
│  (7,806 records)│
└─────────────────┘
```

## Next Steps

- [ ] Deploy backend to cloud (AWS Lambda, Azure Functions, etc.)
- [ ] Add authentication/authorization
- [ ] Implement caching for better performance
- [ ] Add more advanced analytics endpoints
- [ ] Create database integration for faster queries
- [ ] Add data validation and error handling
- [ ] Implement rate limiting

## Credits

© 2025 Nutritional Insights. All Rights Reserved.

**Group 7** — Annie · Komalpreet · Rhailyn Jane
