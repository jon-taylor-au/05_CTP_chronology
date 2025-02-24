import pandas as pd
import time
import datetime
import logging
from llm_class import LLMClient  # Assuming the class file is saved as llm_client.py

# Configuration
INPUT_FILE = "Inputs.xlsx"  # Change as needed
OUTPUT_FILE_TEMPLATE = "output_{timestamp}.xlsx"

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize LLM Client
llm_client = LLMClient()

def process_row(original, prompt):
    """Processes a single row by sending data to the LLM and retrieving the response."""
    try:
        response = llm_client.send_chat_request(original, prompt)
        return response if response else "Error: No response received"
    except Exception as e:
        logging.error(f"Error processing row: {e}")
        return "Error: Exception occurred"

def main():
    """Main function to read input, process rows, and save output."""
    try:
        # Read input spreadsheet
        df = pd.read_excel(INPUT_FILE)

        # Ensure required columns exist
        required_columns = {"original", "prompt"}
        if not required_columns.issubset(df.columns):
            logging.error(f"Input file missing required columns: {required_columns - set(df.columns)}")
            return

        # Process each row
        results = []
        for index, row in df.iterrows():
            logging.info(f"Processing row {index + 1}/{len(df)}")
            response = process_row(row["original"], row["prompt"])
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            results.append([row["original"], row["prompt"], response, timestamp])

        # Create output DataFrame
        output_df = pd.DataFrame(results, columns=["original", "prompt", "response", "timestamp"])

        # Save results to an Excel file with timestamped filename
        output_filename = OUTPUT_FILE_TEMPLATE.format(
            timestamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        )
        output_df.to_excel(output_filename, index=False)
        logging.info(f"Processing complete. Output saved to {output_filename}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
