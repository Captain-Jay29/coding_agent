import sys
import os
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns

def read_csv_file(file_path):
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded data with shape: {df.shape}")
        return df
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except pd.errors.EmptyDataError:
        print(f"Error: File '{file_path}' is empty.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading '{file_path}': {e}")
        sys.exit(1)

def clean_data(df):
    try:
        df_clean = df.drop_duplicates()
        # Fill numeric NaNs with median, categorical with mode
        for col in df_clean.columns:
            if df_clean[col].dtype in ['float64', 'int64']:
                median = df_clean[col].median()
                df_clean[col] = df_clean[col].fillna(median)
            else:
                mode = df_clean[col].mode()
                if not mode.empty:
                    df_clean[col] = df_clean[col].fillna(mode[0])
        print("Data cleaned.")
        return df_clean
    except Exception as e:
        print(f"Error during data cleaning: {e}")
        sys.exit(1)

def generate_visualizations(df, output_dir):
    try:
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_cols:
            plt.figure(figsize=(6,4))
            sns.histplot(df[col], kde=True)
            plt.title(f'Histogram of {col}')
            plt.tight_layout()
            plot_path = os.path.join(output_dir, f"hist_{col}.png")
            plt.savefig(plot_path)
            plt.close()
            print(f"Saved histogram for {col} to {plot_path}")
    except Exception as e:
        print(f"Error generating visualizations: {e}")

def export_to_json(df, output_dir):
    try:
        # Export cleaned data
        cleaned_path = os.path.join(output_dir, "cleaned_data.json")
        df.to_json(cleaned_path, orient='records', lines=True)
        print(f"Cleaned data exported to {cleaned_path}")
        # Export summary statistics
        summary = df.describe(include='all').to_dict()
        summary_path = os.path.join(output_dir, "summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"Summary statistics exported to {summary_path}")
    except Exception as e:
        print(f"Error exporting to JSON: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python data_pipeline.py <csv_file_path> [output_dir]")
        sys.exit(1)
    csv_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    os.makedirs(output_dir, exist_ok=True)

    df = read_csv_file(csv_file)
    df_clean = clean_data(df)
    generate_visualizations(df_clean, output_dir)
    export_to_json(df_clean, output_dir)

if __name__ == "__main__":
    main()
