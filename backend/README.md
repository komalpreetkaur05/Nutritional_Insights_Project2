# Nutritional Insights Backend API

A Flask-based REST API that serves nutritional data from the CSV file.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Health Check
- **GET** `/api/health`
- Returns: Server health status

### Nutrition Summary
- **GET** `/api/nutrition/summary`
- Returns: Aggregated nutrition data by diet type
- Response includes average macronutrients and recipe counts

### Top Protein Recipes
- **GET** `/api/recipes/top-protein?limit=5`
- Parameters: `limit` (optional, default: 5)
- Returns: Top protein-rich recipes with carb content

### Recipe Statistics
- **GET** `/api/recipes?diet_type=keto`
- Parameters: `diet_type` (optional)
- Returns: Recipe statistics, optionally filtered by diet type

### Cluster Analysis
- **GET** `/api/clusters`
- Returns: Diet type clusters based on macronutrient profiles

### All Data (Paginated)
- **GET** `/api/nutrition/all?page=1&per_page=50`
- Parameters: `page` (default: 1), `per_page` (default: 50)
- Returns: Paginated nutrition data

## CORS

CORS is enabled to allow frontend access from any origin during development.

## Data Source

The API reads data from `../Project1Files/All_Diets.csv`
