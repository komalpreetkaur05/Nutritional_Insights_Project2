"""
data_analysis.py
Task 1: Dataset Analysis and Insights

Enhancements:
- Accepts --csv path (default: All_Diets.csv)
- Graceful fallback to aggregated JSON (nutrition_results.json) if CSV is missing
- Optional --no-show flag to suppress interactive plots in headless runs
"""

import argparse
import json
import os

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze diet dataset and produce insights/plots.")
    parser.add_argument(
        "--csv",
        dest="csv_path",
        default="All_Diets.csv",
        help="./All_Diets.csv",
    )
    parser.add_argument(
        "--json",
        dest="json_path",
        default=os.path.join(
            os.path.dirname(__file__),
            "serverless-processing",
            "serverless-processing",
            "simulated_nosql",
            "nutrition_results.json",
        ),
        help="Fallback path to aggregated results JSON if CSV is unavailable.",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Do not call plt.show() (useful in headless/CI runs).",
    )
    return parser.parse_args()


def load_from_csv(csv_path: str) -> pd.DataFrame:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"CSV not found at '{csv_path}'. Place All_Diets.csv in the working directory or pass --csv <path>."
        )
    df = pd.read_csv(csv_path)
    return df


def load_avg_from_json(json_path: str) -> pd.DataFrame:
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON not found at '{json_path}'.")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    avg = data.get("average_macros", [])
    if not avg:
        raise ValueError("average_macros not present in nutrition_results.json")
    # Build a DataFrame consistent with the CSV-derived avg_macros
    avg_macros = pd.DataFrame(avg)
    # Normalize column names to match code below
    avg_macros.rename(
        columns={
            "Protein(g)": "Protein(g)",
            "Carbs(g)": "Carbs(g)",
            "Fat(g)": "Fat(g)",
            "Diet_type": "Diet_type",
        },
        inplace=True,
    )
    avg_macros.set_index("Diet_type", inplace=True)
    return avg_macros


def main():
    args = parse_args()

    recipe_level_available = True
    top_protein = None

    try:
        # 1. Load dataset
        df = load_from_csv(args.csv_path)

        # 2. Handle missing data (fill missing values with mean)
        df = df.fillna(df.mean(numeric_only=True))

        # 3. Calculate the average macronutrient content for each diet type
        avg_macros = (
            df.groupby("Diet_type")[
                ["Protein(g)", "Carbs(g)", "Fat(g)"]
            ].mean()
        )

        print("\n=== Average Macronutrients per Diet Type (from CSV) ===")
        print(avg_macros)

        # 4. Top 5 protein-rich recipes per diet type
        top_protein = (
            df.sort_values("Protein(g)", ascending=False)
            .groupby("Diet_type")
            .head(5)
        )
        print("\n=== Top 5 Protein-Rich Recipes per Diet Type ===")
        print(top_protein[["Diet_type", "Recipe_name", "Protein(g)", "Cuisine_type"]])

        # 5. Diet type with highest protein
        highest_protein = avg_macros["Protein(g)"].idxmax()
        print("\nDiet type with highest protein content:", highest_protein)

        # 6. Most common cuisine per diet type
        common_cuisines = df.groupby("Diet_type")["Cuisine_type"].agg(lambda x: x.mode()[0])
        print("\n=== Most Common Cuisines per Diet Type ===")
        print(common_cuisines)

        # 7. Add new metrics
        df["Protein_to_Carbs_ratio"] = df["Protein(g)"] / df["Carbs(g)"]
        df["Carbs_to_Fat_ratio"] = df["Carbs(g)"] / df["Fat(g)"]

        print("\n=== Sample of New Metrics ===")
        print(
            df[
                [
                    "Diet_type",
                    "Recipe_name",
                    "Protein_to_Carbs_ratio",
                    "Carbs_to_Fat_ratio",
                ]
            ].head()
        )

    except FileNotFoundError as e:
        # Fallback: only aggregated JSON available
        print(f"\n[INFO] {e}")
        print("[INFO] Falling back to aggregated JSON results for average macros …")
        recipe_level_available = False
        avg_macros = load_avg_from_json(args.json_path)
        print("\n=== Average Macronutrients per Diet Type (from JSON) ===")
        print(avg_macros)

    # 8. Visualizations
    # Bar Chart – Average Protein
    plt.figure(figsize=(8, 5))
    sns.barplot(x=avg_macros.index, y=avg_macros["Protein(g)"])
    plt.title("Average Protein by Diet Type")
    plt.ylabel("Average Protein (g)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("avg_protein_by_diet_type.png")
    if not args.no_show:
        plt.show()

    # Heatmap – Macronutrients
    plt.figure(figsize=(8, 5))
    sns.heatmap(avg_macros, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Average Macronutrients by Diet Type")
    plt.tight_layout()
    plt.savefig("avg_macros_heatmap.png")
    if not args.no_show:
        plt.show()

    # Scatter Plot – Top Protein Recipes (only if recipe-level data available)
    if recipe_level_available and top_protein is not None:
        plt.figure(figsize=(8, 5))
        sns.scatterplot(
            data=top_protein,
            x="Protein(g)",
            y="Carbs(g)",
            hue="Diet_type",
            style="Cuisine_type",
        )
        plt.title("Top 5 Protein-rich Recipes by Diet Type")
        plt.tight_layout()
        plt.savefig("top_protein_recipes_scatter.png")
        if not args.no_show:
            plt.show()
    else:
        print(
            "\n[INFO] Skipping scatter plot for top protein recipes because recipe-level CSV data is not available."
        )


if __name__ == "__main__":
    main()
