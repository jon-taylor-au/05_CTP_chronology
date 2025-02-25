import pandas as pd
import datetime
import logging
from llm_class import LLMClient  # Assuming the class file is saved as llm_class.py
import os
import glob
import csv

# --- Custom CSV Log Handler ---
class CSVLogHandler(logging.Handler):
    """
    Custom logging handler that writes log messages to a CSV file.
    Each log row will contain: timestamp, log level, and message.
    """
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        # If the file doesn't exist, create it and write the header row.
        if not os.path.exists(filename):
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "level", "message"])

    def emit(self, record):
        try:
            # Create a formatted timestamp
            timestamp = datetime.datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
            level = record.levelname
            message = self.format(record)
            with open(self.filename, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([timestamp, level, message])
        except Exception:
            self.handleError(record)

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()
csv_handler = CSVLogHandler("run_logs.csv")
csv_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
csv_handler.setFormatter(formatter)
logger.addHandler(csv_handler)

# --- File Lookup ---
# Get all files that contain "courtbook.csv" in their name
courtbook_files = glob.glob("*courtbook.csv")
# Get all files that contain "chronology.csv" in their name (for fast lookup)
chronology_files = set(glob.glob("*chronology.csv"))

# --- LLM Processing Functions ---
def process_row(original, prompt):
    """Processes a single row by sending data to the LLM and retrieving the response."""
    try:
        response = llm_client.send_chat_request(original, prompt)
        return response if response else "Error: No response received"
    except Exception as e:
        logging.error(f"Error processing row: {e}")
        return "Error: Exception occurred"

def process_courtbook_file(input_file, prompt_file, output_file):
    """
    Reads an input CSV (with columns Entry_Original and PromptID),
    looks up the prompt text from prompt_file (CSV with prompt_id and prompt_text),
    processes each row via the LLM, and saves the results to output_file.
    """
    try:
        # Read the input CSV file
        df = pd.read_csv(input_file)
        required_input_columns = {"Entry_Original", "PromptID"}
        if not required_input_columns.issubset(df.columns):
            missing = required_input_columns - set(df.columns)
            logging.error(f"Input file {input_file} missing required columns: {missing}")
            return

        # Read the prompt lookup CSV file
        prompt_df = pd.read_csv(prompt_file)
        required_prompt_columns = {"prompt_id", "prompt_text"}
        if not required_prompt_columns.issubset(prompt_df.columns):
            missing = required_prompt_columns - set(prompt_df.columns)
            logging.error(f"Prompt file {prompt_file} missing required columns: {missing}")
            return

        # Create a dictionary mapping prompt_id to prompt_text
        prompt_dict = dict(zip(prompt_df["prompt_id"], prompt_df["prompt_text"]))
        
        results = []
        # Process each row in the input file
        for index, row in df.iterrows():
            logging.info(f"Processing row {index + 1}/{len(df)} in file {input_file}")
            original = row["Entry_Original"]
            prompt_id = row["PromptID"]
            prompt_text = prompt_dict.get(prompt_id)
            if prompt_text is None:
                logging.error(f"No prompt found for PromptID: {prompt_id}")
                response = "Error: No prompt found"
            else:
                response = process_row(original, prompt_text)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            results.append([original, prompt_id, prompt_text, response, timestamp])
        
        # Create output DataFrame with appropriate column names
        output_df = pd.DataFrame(results, 
                                 columns=["Entry_Original", "PromptID", "PromptText", "Response", "Timestamp"])
        output_df.to_csv(output_file, index=False)
        logging.info(f"Processing complete for {input_file}. Output saved to {output_file}")
    except Exception as e:
        logging.error(f"Unexpected error processing {input_file}: {e}")

# --- Main Processing ---
# Initialize LLM Client
llm_client = LLMClient()

def main():
    PROMPT_FILE = "prompt_list.csv"  # CSV with columns prompt_id and prompt_text

    # Process each courtbook file that does NOT have a corresponding chronology file.
    for cb_file in courtbook_files:
        expected_chronology = cb_file.replace("courtbook.csv", "chronology.csv")
        if expected_chronology not in chronology_files:
            logging.info(f"Processing file: {cb_file} (missing corresponding chronology file)")
            process_courtbook_file(cb_file, PROMPT_FILE, expected_chronology)
        else:
            logging.info(f"Skipping {cb_file}; corresponding chronology file exists: {expected_chronology}")

if __name__ == "__main__":
    main()
