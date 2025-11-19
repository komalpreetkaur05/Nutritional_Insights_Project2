"""
Nutritional Insights Backend API
--------------------------------

A minimal Flask server that exposes REST endpoints backed by a CSV file
(`All_Diets.csv`) to provide aggregated nutrition insights and basic
exploratory data APIs used by the frontend dashboard.

Key responsibilities
- Load the nutrition dataset from disk (via pandas) on-demand per request
- Provide summarized macronutrients by diet type
- Return top protein-rich recipes (for scatter plot)
- Offer simple cluster-like groupings (demo) based on macronutrient profiles
- Support pagination for accessing raw/complete data

Notes
- This service keeps state out of memory; each request reads the CSV. For
    higher throughput, consider caching the loaded DataFrame (with invalidation)
    or persisting to a database.
- All endpoints return JSON with a consistent `status` field on success.
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
# Enable CORS so the browser can call this API from the frontend served as a
# static file (e.g., opened directly in a browser) without same-origin issues.
CORS(app)

# Path to the source CSV file. Prefer an environment override via `CSV_PATH`;
# otherwise, resolve relative to this file so the backend can be started from
# the project root or the `backend/` directory.
CSV_PATH = os.getenv('CSV_PATH') or os.path.join(
    os.path.dirname(__file__), '..', 'All_Diets.csv'
)

def load_nutrition_data():
    """Load the nutrition dataset from the CSV into a pandas DataFrame.

    Expected CSV columns (minimum):
    - 'Diet_type' (str): diet category label
    - 'Recipe_name' (str): recipe title/name
    - 'Protein(g)' (float): protein content in grams
    - 'Carbs(g)' (float): carbs content in grams
    - 'Fat(g)' (float): fat content in grams

    Returns
    -------
    pandas.DataFrame | None
        The loaded DataFrame on success, or None if the file is missing or
        unreadable (e.g., empty or malformed).
    """
    try:
        df = pd.read_csv(CSV_PATH)
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError) as e:
        print(f"Error loading CSV: {e}")
        return None

def calculate_diet_summary(df):
    """Calculate average macronutrients and recipe counts by diet type.

    Parameters
    ----------
    df : pandas.DataFrame
        The full dataset loaded from the CSV.

    Returns
    -------
    list[dict]
        Records shaped for the frontend:
        [{ 'Diet_type': str, 'Protein': float, 'Carbs': float, 'Fat': float, 'recipes': int }]
    """
    summary = df.groupby('Diet_type').agg({
        'Protein(g)': 'mean',
        'Carbs(g)': 'mean',
        'Fat(g)': 'mean',
        'Recipe_name': 'count'
    }).reset_index()

    summary.columns = ['Diet_type', 'Protein', 'Carbs', 'Fat', 'recipes']

    return summary.to_dict('records')

def get_top_protein_recipes(df, limit=5):
    """Return the top-N protein-rich recipes for scatter plotting.

    Parameters
    ----------
    df : pandas.DataFrame
        The full dataset.
    limit : int, optional
        Number of top recipes to return (default 5).

    Returns
    -------
    list[dict]
        [{ 'recipe': str, 'protein': float, 'carbs': float }]
    """
    cols = ['Recipe_name', 'Protein(g)', 'Carbs(g)']
    top_recipes = df.nlargest(limit, 'Protein(g)')[cols]

    result = []
    for _, row in top_recipes.iterrows():
        result.append({
            'recipe': row['Recipe_name'],
            'protein': round(row['Protein(g)'], 1),
            'carbs': round(row['Carbs(g)'], 1)
        })

    return result

@app.route('/api/health', methods=['GET'])
def health_check():
    """Lightweight health probe to verify the API is responsive."""
    return jsonify({
        'status': 'healthy',
        'message': 'Nutritional Insights API is running'
    })

@app.route('/api/nutrition/summary', methods=['GET'])
def get_nutrition_summary():
    """Get aggregated macronutrient means and counts by diet type.

    Response shape
    --------------
    {
        'status': 'success',
        'total_records': int,
        'diet_types': int,
        'data': [
            {
                'Diet_type': str,
                'Protein': float,
                'Carbs': float,
                'Fat': float,
                'recipes': int
            },
            ...
        ]
    }
    """
    df = load_nutrition_data()

    if df is None:
        return jsonify({'error': 'Failed to load data'}), 500

    diet_summary = calculate_diet_summary(df)

    return jsonify({
        'status': 'success',
        'total_records': len(df),
        'diet_types': len(diet_summary),
        'data': diet_summary
    })

@app.route('/api/recipes/top-protein', methods=['GET'])
def get_top_protein():
    """Get top protein-rich recipes.

    Query params
    ------------
    - limit: int (optional, default=5) number of recipes to return
    """
    limit = request.args.get('limit', default=5, type=int)

    df = load_nutrition_data()

    if df is None:
        return jsonify({'error': 'Failed to load data'}), 500

    top_recipes = get_top_protein_recipes(df, limit)

    return jsonify({
        'status': 'success',
        'count': len(top_recipes),
        'data': top_recipes
    })

@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    """Return recipe statistics with optional diet-type filtering.

    Query params
    ------------
    - diet_type: str (optional) exact diet type label to filter by

    Response shape
    --------------
    {
        'status': 'success',
        'statistics': {
            'total_recipes': int,
            'avg_protein': float,
            'avg_carbs': float,
            'avg_fat': float
        }
    }
    """
    df = load_nutrition_data()

    if df is None:
        return jsonify({'error': 'Failed to load data'}), 500

    # Optional diet type filter
    diet_type = request.args.get('diet_type')
    if diet_type:
        df = df[df['Diet_type'].str.lower() == diet_type.lower()]

    # Calculate statistics
    stats = {
        'total_recipes': len(df),
        'avg_protein': round(df['Protein(g)'].mean(), 2),
        'avg_carbs': round(df['Carbs(g)'].mean(), 2),
        'avg_fat': round(df['Fat(g)'].mean(), 2)
    }

    return jsonify({
        'status': 'success',
        'statistics': stats
    })

@app.route('/api/clusters', methods=['GET'])
def get_clusters():
    """Return a simple, heuristic "cluster" grouping of diet types.

    This is a demonstration-only feature that partitions diet types into
    three buckets using fixed thresholds on mean macronutrient values:
    - high_protein: Protein > 90 g
    - high_carb:    Carbs > 200 g
    - balanced:     everything else
    """
    df = load_nutrition_data()

    if df is None:
        return jsonify({'error': 'Failed to load data'}), 500

    summary = calculate_diet_summary(df)

    # Simple clustering logic based on macronutrient profiles
    high_protein = [d['Diet_type'] for d in summary if d['Protein'] > 90]
    high_carb = [d['Diet_type'] for d in summary if d['Carbs'] > 200]
    balanced = [
        d['Diet_type'] for d in summary
        if d['Diet_type'] not in high_protein
        and d['Diet_type'] not in high_carb
    ]

    return jsonify({
        'status': 'success',
        'clusters_identified': 3,
        'high_protein_cluster': high_protein,
        'high_carb_cluster': high_carb,
        'balanced_cluster': balanced
    })

@app.route('/api/nutrition/all', methods=['GET'])
def get_all_data():
    """Return the complete dataset (raw rows) with server-side pagination.

    Query params
    ------------
    - page: int (default=1)     1-based page number
    - per_page: int (default=50) number of rows per page

    Response shape
    --------------
    {
        'status': 'success',
        'page': int,
        'per_page': int,
        'total_records': int,
        'total_pages': int,
        'data': [ {row...}, ... ]
    }
    """
    df = load_nutrition_data()

    if df is None:
        return jsonify({'error': 'Failed to load data'}), 500

    # Pagination parameters
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=50, type=int)

    # Calculate pagination
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    total_records = len(df)
    total_pages = (total_records + per_page - 1) // per_page

    # Get page data
    page_data = df.iloc[start_idx:end_idx].to_dict('records')

    return jsonify({
        'status': 'success',
        'page': page,
        'per_page': per_page,
        'total_records': total_records,
        'total_pages': total_pages,
        'data': page_data
    })

if __name__ == '__main__':
    # Run the Flask app
    print("Starting Nutritional Insights API...")
    print(f"CSV Path: {CSV_PATH}")
    # Use environment variable to control debug mode
    # For production, set FLASK_ENV=production
    debug_mode = (
        os.getenv('FLASK_DEBUG', '0') == '1' or
        os.getenv('FLASK_ENV', 'development') == 'development'
    )

    HOST_BIND = os.getenv('HOST', '127.0.0.1')
    try:
        PORT = int(os.getenv('PORT', '5000'))
    except ValueError:
        print("Invalid PORT in environment; defaulting to 5000")
        PORT = 5000

    app.run(debug=debug_mode, host=HOST_BIND, port=PORT)
