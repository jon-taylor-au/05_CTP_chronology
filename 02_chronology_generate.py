import pandas as pd
import datetime
import logging
import re
from supporting_files.llm_class import LLMClient  # Custom LLM Client
import os
import glob
import csv

# CONSTANTS
OUTPUT_LOCATION = 'outputs/'  # Folder to save the output files
SUPPORT_LOCATION = 'supporting_files/'  # Folder containing support files

# --- Custom CSV Log Handler ---
class CSVLogHandler(logging.Handler):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        if not os.path.exists(filename):
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "level", "message"])

    def emit(self, record):
        try:
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
csv_handler = CSVLogHandler(f"{OUTPUT_LOCATION}run_logs.csv")
csv_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
csv_handler.setFormatter(formatter)
logger.addHandler(csv_handler)

# --- File Lookup ---
courtbook_files = glob.glob(f"{OUTPUT_LOCATION}*courtbook.csv")
chronology_files = set(glob.glob(f"{OUTPUT_LOCATION}*chronology.csv"))

# --- LLM Processing Functions ---
def extract_bullet_points(response):
    """Extracts bullet points and sub-bullets from the response if present, otherwise returns 'Inconclusive Response'."""
    bullet_pattern = re.findall(r"(?:^|\n)\s*[*\-•→]+\s+.*", response)  # Allows spaces/tabs before bullets
    
    if bullet_pattern:
        return "In Summary\n" + "\n".join(bullet_pattern)
    else:
        return "Inconclusive Response"# + response 

def process_row(original, prompt):
    """Processes a single row by sending data to the LLM and retrieving the response."""
    try:
        response = llm_client.send_chat_request(original, prompt)
        if response:
            return extract_bullet_points(response)
        return "Error: No response received"
    except Exception as e:
        logging.error(f"Error processing row: {e}")
        return "Error: Exception occurred"

def process_courtbook_file(input_file, prompt_file, output_file):
    try:
        df = pd.read_csv(input_file)
        required_input_columns = {"Entry_Original", "PromptID"}
        if not required_input_columns.issubset(df.columns):
            missing = required_input_columns - set(df.columns)
            logging.error(f"Input file {input_file} missing required columns: {missing}")
            return

        prompt_df = pd.read_csv(prompt_file)
        required_prompt_columns = {"prompt_id", "prompt_text"}
        if not required_prompt_columns.issubset(prompt_df.columns):
            missing = required_prompt_columns - set(prompt_df.columns)
            logging.error(f"Prompt file {prompt_file} missing required columns: {missing}")
            return

        prompt_dict = dict(zip(prompt_df["prompt_id"], prompt_df["prompt_text"]))
        results = []

        for index, row in df.iterrows():
            logging.info(f"Processing row {index + 1}/{len(df)} in file {input_file}")
            entry_date = row["Entry Date"]
            entry_description = row["Entry Description"]
            original = row["Entry_Original"]
            prompt_id = row["PromptID"]
            prompt_text = prompt_dict.get(prompt_id)
            
            if prompt_text is None:
                logging.error(f"No prompt found for PromptID: {prompt_id}")
                response = "Error: No prompt found"
            else:
                response = process_row(original, prompt_text)
            
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            results.append([entry_date, entry_description, original, response, timestamp])

        output_df = pd.DataFrame(results, columns=["Entry Date", "Entry Description","Entry_Original", "Response", "Timestamp"])
        output_df.to_csv(output_file, index=False)
        logging.info(f"Processing complete for {input_file}. Output saved to {output_file}")
    except Exception as e:
        logging.error(f"Unexpected error processing {input_file}: {e}")

# --- Main Processing ---
llm_client = LLMClient()

def main():
    PROMPT_FILE = f"{SUPPORT_LOCATION}prompt_list.csv"
    for cb_file in courtbook_files:
        expected_chronology = cb_file.replace("courtbook.csv", "chronology.csv")
        if expected_chronology not in chronology_files:
            logging.info(f"Processing file: {cb_file} (missing corresponding chronology file)")
            process_courtbook_file(cb_file, PROMPT_FILE, expected_chronology)
        else:
            logging.info(f"Skipping {cb_file}; corresponding chronology file exists: {expected_chronology}")

if __name__ == "__main__":
    main()
