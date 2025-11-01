from azure.storage.blob import BlobServiceClient
import pandas as pd
import io
import json
import os
from datetime import datetime

def process_nutritional_data_from_azurite():
    """
    Serverless function to process nutritional data from Azurite Blob Storage
    """
    try:
        print(f"[{datetime.now()}] Starting serverless function execution...")
        
        # Azurite connection string
        connect_str = (
            "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;"
            "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
            "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
        )
        
        print(f"[{datetime.now()}] Connecting to Azurite Blob Storage...")
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        
        container_name = 'datasets'
        blob_name = 'All_Diets.csv'
        
        print(f"[{datetime.now()}] Accessing container: {container_name}, blob: {blob_name}")
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)
        
        # Check if blob exists
        if not blob_client.exists():
            raise Exception(f"Blob {blob_name} not found in container {container_name}")
        
        # Download blob content
        print(f"[{datetime.now()}] Downloading CSV data...")
        stream = blob_client.download_blob().readall()
        
        # Read CSV data
        print(f"[{datetime.now()}] Processing CSV data...")
        df = pd.read_csv(io.BytesIO(stream))
        
        # Display basic info about the dataset
        print(f"[{datetime.now()}] Dataset shape: {df.shape}")
        print(f"[{datetime.now()}] Columns: {list(df.columns)}")
        print(f"[{datetime.now()}] Diet types found: {df['Diet_type'].unique()}")
        
        # Calculate average nutritional values per diet type
        print(f"[{datetime.now()}] Calculating average macros per diet type...")
        avg_macros = df.groupby('Diet_type')[['Protein(g)', 'Carbs(g)', 'Fat(g)']].mean().round(2)
        
        # Create results directory if it doesn't exist
        os.makedirs('simulated_nosql', exist_ok=True)
        
        # Prepare results for JSON storage
        result = avg_macros.reset_index().to_dict(orient='records')
        
        # Add metadata
        results_with_metadata = {
            "processing_timestamp": datetime.now().isoformat(),
            "source_file": blob_name,
            "total_records_processed": len(df),
            "diet_types_analyzed": avg_macros.index.tolist(),
            "average_macros": result
        }
        
        # Save to JSON file (simulating NoSQL database)
        output_file = 'simulated_nosql/nutrition_results.json'
        with open(output_file, 'w') as f:
            json.dump(results_with_metadata, f, indent=2)
        
        print(f"[{datetime.now()}] Results saved to: {output_file}")
        
        # Print summary to console
        print("\n" + "="*50)
        print("PROCESSING SUMMARY")
        print("="*50)
        for diet in result:
            print(f"Diet: {diet['Diet_type']}")
            print(f"  Avg Protein: {diet['Protein(g)']}g")
            print(f"  Avg Carbs: {diet['Carbs(g)']}g")
            print(f"  Avg Fat: {diet['Fat(g)']}g")
            print()
        
        return {
            "status": "success",
            "message": f"Processed {len(df)} records from {blob_name}",
            "output_file": output_file,
            "diet_types_analyzed": len(result)
        }
        
    except Exception as e:
        error_msg = f"Error processing data: {str(e)}"
        print(f"[{datetime.now()}] {error_msg}")
        return {
            "status": "error",
            "message": error_msg
        }

if __name__ == "__main__":
    result = process_nutritional_data_from_azurite()
    print(f"\nExecution completed: {result}")
