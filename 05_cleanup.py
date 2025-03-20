import os
import glob
import logging

# Constants
OUTPUT_LOCATION = "outputs/"  # Folder containing the CSV files
FILE_PATTERN = "*_part*.csv"  # Pattern to match part files

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def cleanup_part_files():
    """Deletes all CSV files with 'part' in the filename."""
    part_files = glob.glob(os.path.join(OUTPUT_LOCATION, FILE_PATTERN))
    
    if not part_files:
        logging.info("No part files found for deletion.")
        return
    
    for file in part_files:
        try:
            os.remove(file)
            logging.info(f"Deleted: {file}")
        except Exception as e:
            logging.error(f"Error deleting {file}: {e}")

if __name__ == "__main__":
    cleanup_part_files()