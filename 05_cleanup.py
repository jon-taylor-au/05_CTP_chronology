import os
import glob
import logging
import shutil
import zipfile

# Constants
OUTPUT_LOCATION = "outputs/"  # Folder containing files to clean up
ARCHIVE_LOCATION = "archives/"  # Folder for archived files
FILE_PATTERN = "*_part*.csv"  # Pattern to match part files
ZIP_FILENAME_TEMPLATE = "{court_book_id}_archived_outputs.zip"  # Name of the archive file

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def zip_and_move_output(court_book_id):
    """Zips all files in OUTPUT_LOCATION and moves the zip file to ARCHIVE_LOCATION."""
    zip_filename = ZIP_FILENAME_TEMPLATE.format(court_book_id=court_book_id)
    zip_path = os.path.join(ARCHIVE_LOCATION, zip_filename)
    
    # Ensure archive directory exists
    os.makedirs(ARCHIVE_LOCATION, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for foldername, subfolders, filenames in os.walk(OUTPUT_LOCATION):
            if foldername.startswith(ARCHIVE_LOCATION):
                continue  # Skip archiving the archive folder itself
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                if file_path != zip_path:  # Avoid adding the zip file itself
                    zipf.write(file_path, os.path.relpath(file_path, OUTPUT_LOCATION))
    
    logging.info(f"Zipped all output files and moved to {zip_path}")

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

def delete_output_contents():
    """Deletes all files in the OUTPUT_LOCATION after archiving."""
    for file in glob.glob(os.path.join(OUTPUT_LOCATION, '*')):
        try:
            if os.path.isfile(file):
                os.remove(file)
                logging.info(f"Deleted: {file}")
            elif os.path.isdir(file):
                shutil.rmtree(file)
                logging.info(f"Deleted directory: {file}")
        except Exception as e:
            logging.error(f"Error deleting {file}: {e}")

if __name__ == "__main__":
    cleanup_part_files()
    court_book_id = input("Enter Court Book ID for archive prefix: ").strip()
    zip_and_move_output(court_book_id)
    delete_output_contents()
    
