import pandas as pd
import glob
import os
import logging
import re

# Constants
OUTPUT_LOCATION = "outputs/"  # Folder containing part files
FILE_PATTERN = "*_part*.csv"  # Pattern to match all part files

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def clean_response(text):
    """Cleans the 'Response' text by removing unnecessary bullet points and formatting."""
    if not isinstance(text, str):
        return text  # Return as-is if not a string
    
    # Remove extra spaces between bullet points
    text = re.sub(r"\n\s*[*\-•→]+", "\n*", text)
    
    # Remove unwanted bullet points
    lines = text.split("\n")
    cleaned_lines = [
        line for line in lines
        if not line.startswith("BrewChat")
        and "XML" not in line
        and not line.startswith("Dates are answered in the format")
    ]
    
    # Replace "â€¢" with "*"
    cleaned_text = "\n".join(cleaned_lines).replace("â€¢", "*")
    
    return cleaned_text


def concatenate_parts():
    """Concatenates all part CSV files into a single final CSV per court book and recombines entries with the same Unique ID."""
    part_files = glob.glob(os.path.join(OUTPUT_LOCATION, FILE_PATTERN))
    
    if not part_files:
        logging.info("No part files found for concatenation.")
        return
    
    # Group part files by court book ID (extract ID before '_part')
    courtbook_groups = {}
    for file in part_files:
        base_name = os.path.basename(file)
        courtbook_id = base_name.split("_part")[0]  # Extract courtbook ID
        courtbook_groups.setdefault(courtbook_id, []).append(file)
    
    # Process each court book
    for courtbook_id, files in courtbook_groups.items():
        files.sort()  # Ensure proper order (part1, part2, etc.)
        logging.info(f"Merging {len(files)} parts for court book {courtbook_id}")
        
        # Concatenate CSV files
        df_list = [pd.read_csv(f) for f in files]
        final_df = pd.concat(df_list, ignore_index=True)
        
        # Clean 'Response' column
        if "Response" in final_df.columns:
            final_df["Response"] = final_df["Response"].apply(clean_response)
        
        # Remove 'Part' column
        if "Part" in final_df.columns:
            final_df.drop(columns=["Part"], inplace=True)
        
        # Recombine entries with the same Unique ID
        if "UniqueID" in final_df.columns:
            final_df = final_df.groupby("UniqueID", as_index=False).agg({
                "EntryDate": "first",  # Keep the first date
                "EntryDescription": "first",  # Keep the first description
                "EntryOriginal": "first",  # Keep the first original entry
                "Response": " \n".join,  # Concatenate responses
                "Handwritten": "first",  # Keep the first handwritten value
                "TimeProcessed": "first"  # Keep the first processed time
            })
        
        # Save the merged file
        final_filename = os.path.join(OUTPUT_LOCATION, f"{courtbook_id}_chronology.csv")
        final_df.to_csv(final_filename, index=False)
        logging.info(f"Saved merged file: {final_filename}")
    

if __name__ == "__main__":
    concatenate_parts()
