# CTP Chronology Processing

## Overview
This project automates the extraction, processing, and cleanup of court book data, generating structured outputs in CSV and Excel formats. The workflow consists of multiple scripts that handle different stages of processing.

## Project Structure
```
CTP_chronology/
│   .env                    # Environment variables (if applicable)
│   .gitignore              # Ignore unnecessary files
│   00_courtbooks_to_get.csv  # Input list of court book IDs
│   01_webapp_extract_data.py  # Extracts court book data from API
│   02_chronology_generate.py  # Processes extracted data into structured chronology
│   03_post_process.py         # Cleans and formats the processed data
│   04_cleanup.py              # Deletes temporary part files
│   debug.log                  # Log file for debugging
│
├───outputs/
│       11661_chronology.xlsx  # Final structured output (Excel format)
│       11661_courtbook.csv    # Raw extracted court book data
│
└───supporting_files/
    │   llm_class.py          # Handles communication with the LLM
    │   prompt_list.csv       # List of prompts for LLM processing
    │   webapp_class.py       # API client for fetching court book data
    │   windows_run_scripts.bat  # Script for running the project on Windows
    │
    └───__pycache__/          # Compiled Python files
```

## Installation & Setup
### **Prerequisites**
- Python 3.11+
- Required Python libraries (install with `pip install -r requirements.txt` if applicable)

### **Setup**
1. Clone the repository:
   ```sh
   git clone <repository_url>
   cd CTP_chronology
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt  # If a requirements.txt file exists
   ```
3. Configure `.env` (if applicable).

## Script Descriptions
### **1. Extract Data** (`01_webapp_extract_data.py`)
- Fetches court book data from an API.
- Cleans and structures the extracted data.
- Saves raw data to `outputs/`.

## **Detailed Explanation of `01_webapp_extract_data.py`**

### **📌 Overview**
This script is responsible for **fetching, processing, and storing court book data** from an API. It ensures that only **relevant and non-handwritten** records are processed and saves them as CSV files.

---

## **🔹 Key Features**
- **Extracts** data from an API using `APIClient`.
- **Cleans HTML content** to extract meaningful text.
- **Filters** entries to only include **"Handwritten" == "false"** and **"Relevant" == "Relevant"**.
- **Splits long entries** into multiple parts if needed.
- **Generates unique IDs** for each entry to track split parts.
- **Saves** structured data into CSV files.

---

## **🔎 Step-by-Step Breakdown**

### **1️⃣ Constants & Imports**
```python
BASE_URL = "http://sydwebdev139:8080"
LOGIN_PAGE_URL = f"{BASE_URL}/sparke/authed/user.action?cmd=welcome"
LOGIN_URL = f"{BASE_URL}/sparke/authed/j_security_check"
CSV_FILE = '00_courtbooks_to_get.csv'
OUTPUT_LOCATION = 'outputs/'
```
- Defines the **API endpoint URLs** for fetching court book data.
- Specifies the **input CSV file** (`00_courtbooks_to_get.csv`) that contains court book IDs.
- Sets the **output folder** for storing the processed CSV files.

---

### **2️⃣ Extract First Line from HTML**
```python
def extract_first_line(text, max_length=80):
    """Extracts the first non-empty line of text from <p> tags in an HTML string and truncates it."""
```
- **Parses HTML** to extract the first meaningful `<p>` tag.
- **Trims text to 80 characters**, adding `...` if it's too long.

💡 **Why?**  
Court book entries contain HTML, and we need to extract only the first **meaningful** line.

---

### **3️⃣ Split Text into Parts**
```python
def split_text_into_parts(text, num_parts):
    """Splits text into roughly equal parts, keeping sentence integrity if possible."""
```
- Splits long text **evenly** based on **word count**.
- Ensures each split **maintains sentence integrity** where possible.

💡 **Why?**  
If an entry **exceeds** the `TOKEN_LIMIT` (**3500 tokens**), it needs to be **broken into multiple parts**.

---

### **4️⃣ Parse API Data**
```python
def parse_data(data):
    """Processes API response into structured rows for CSV output, including split text parts."""
```
- Loops through each **court book entry** received from the API.
- **Filters out** records where:
  ```python
  if handwritten != "false" or relevant != "Relevant":
      continue  # Skip this entry
  ```
  Only **"Handwritten" == "false"** and **"Relevant" == "Relevant"** records are processed.
- **Extracts key details**:
  - **Entry Date**
  - **Cleaned Text (`entryOriginal`)**
  - **First Line (short summary)**
  - **Token Count Estimate**
- **Splits large entries** into multiple parts if needed.
- **Assigns a Unique ID** (`uuid4`) to each entry.

💡 **Why?**  
This step ensures **only relevant data** is processed and stored.

---

### **5️⃣ Save Data as CSV**
```python
def save_to_csv(rows, court_book_id):
    """Saves processed data to a CSV file."""
```
- Converts processed data to a **Pandas DataFrame**.
- **Reorders columns** for clarity:
  ```python
  cols = ["Index", "Unique ID","Part", "First Line", "Handwritten", "Relevant", "Court Book ID", "Book Item ID", "Entry Date", "PromptID", "Entry_Original", "Token Count", "Entry Description"]
  ```
- **Saves the CSV file** under `outputs/`.

💡 **Why?**  
Ensures structured storage of extracted court book data.

---

### **6️⃣ Fetch API Data & Process**
```python
def process_court_book(client, court_book_id):
    """Fetches court book data and writes it to CSV."""
```
- Calls the API using `client.fetch_api_data()`.
- Runs **`parse_data()`** to process the response.
- Saves the structured data using **`save_to_csv()`**.

---

### **7️⃣ Main Execution**
```python
def main():
    """Main function to process court books from the CSV file."""
```
- **Authenticates with API** using `APIClient`.
- Reads `00_courtbooks_to_get.csv` to get a list of **court book IDs**.
- **Checks if a file already exists**, skipping if necessary.
- **Processes each court book ID** and saves results.

---

## **🚀 How It Fits Into the Workflow**
✅ **Step 1: Extracts** data from API  
✅ **Step 2: Filters** handwritten/relevant records  
✅ **Step 3: Cleans** text (HTML parsing)  
✅ **Step 4: Splits** long entries into **manageable parts**  
✅ **Step 5: Saves** structured CSV output  

---

## **🔹 Summary**
| Feature                 | Description |
|------------------------|-------------|
| **Extracts Data** | Fetches court book data from API |
| **Filters Data** | Keeps only non-handwritten and relevant records |
| **Cleans HTML** | Extracts meaningful text from `<p>` tags |
| **Splits Large Entries** | Ensures no entry exceeds `TOKEN_LIMIT` (3500 tokens) |
| **Generates Unique IDs** | Tracks each entry and its split parts |
| **Saves as CSV** | Outputs structured data for further processing |

---


### **2. Generate Chronology** (`02_chronology_generate.py`)
- Processes extracted data into structured chronological records.
- Splits large entries into multiple parts.
- Generates a `courtbook.csv` file.

## **Detailed Explanation of `02_chronology_generate.py`**

### **📌 Overview**
This script processes extracted court book data by:
- Splitting data into manageable **batches** for processing.
- **Sending entries** to an LLM for summarization.
- Extracting and **structuring** responses.
- Storing results in **batch CSV files**.

---

## **🔹 Key Features**
- **Splits records** into batches (`RECORDS_TO_PROCESS` per file) to prevent overload.
- **Sends prompts to an LLM** for processing.
- **Extracts bullet points** from LLM responses.
- **Handles errors** and logs processing details.
- **Saves structured outputs** as part files (`part1.csv`, `part2.csv`, etc.).

---

## **🔎 Step-by-Step Breakdown**

### **1️⃣ Constants & Imports**
```python
OUTPUT_LOCATION = 'outputs/'  # Folder to save the output files
SUPPORT_LOCATION = 'supporting_files/'  # Folder containing support files
RECORDS_TO_PROCESS = 2  # Number of records to process in each file
```
- Defines the number of **records to process per batch** (`RECORDS_TO_PROCESS`).
- Sets paths for **input and output files**.

---

### **2️⃣ Custom CSV Logger**
```python
class CSVLogHandler(logging.Handler):
```
- **Stores logs in CSV format** instead of text logs.
- Ensures that log entries include:
  - **Timestamp**
  - **Log Level (INFO, ERROR, etc.)**
  - **Message**

💡 **Why?**  
This allows easy tracking of errors and processing details in a structured format.

---

### **3️⃣ Extract Bullet Points from LLM Responses**
```python
def extract_bullet_points(response):
```
- Uses **Regex** to extract bullet points (`*`, `-`, `•` symbols) from LLM responses.
- If no structured bullets are found, returns `"Inconclusive Response"`.

💡 **Why?**  
Ensures that responses are properly formatted for easy reading.

---

### **4️⃣ Send Entries to LLM**
```python
def process_row(original, prompt):
```
- Sends the original entry to the LLM for processing.
- Extracts and structures the response.
- Returns `"Error: No response received"` if the LLM fails.

💡 **Why?**  
Handles LLM failures gracefully and prevents empty or unusable responses.

---

### **5️⃣ Process Each Court Book File**
```python
def process_courtbook_file(input_file, prompt_file, output_prefix):
```
- **Reads the input file (`courtbook.csv`)** to process structured entries.
- Ensures required columns are present.
- Splits the data into **batches of `RECORDS_TO_PROCESS`**.
- **Processes each batch separately** to generate responses.
- Saves results to `partX.csv` files.

💡 **Why?**  
Splitting into smaller batches prevents **overloading the LLM** and ensures efficient processing.

---

### **6️⃣ Main Execution Loop**
```python
def main():
```
- Loops through **all extracted court book files (`*_courtbook.csv`)**.
- **Skips files that are already processed (`*_chronology.csv`).**
- Calls `process_courtbook_file()` for missing ones.

💡 **Why?**  
Prevents duplicate processing and ensures only unprocessed files are handled.

---

## **🚀 How It Fits Into the Workflow**
✅ **Step 1: Reads Extracted Data (`*_courtbook.csv`)**  
✅ **Step 2: Splits Entries Into Batches**  
✅ **Step 3: Sends Each Entry to the LLM**  
✅ **Step 4: Extracts & Structures Responses**  
✅ **Step 5: Saves Each Batch as a `partX.csv` File**  

---

## **🔹 Summary**
| Feature                 | Description |
|------------------------|-------------|
| **Batch Processing** | Splits large datasets into smaller parts |
| **LLM Integration** | Sends entries to LLM for structured responses |
| **Response Cleaning** | Extracts only meaningful bullet points |
| **Structured Logging** | Logs all processing details in CSV format |
| **Avoids Duplicates** | Skips processing already completed files |

---

### **3. Post-Process Data** (`03_post_process.py`)
- Merges part files into a single `chronology.xlsx` file.
- Cleans up formatting and ensures structured output.
- Applies Excel formatting (e.g., column width, text wrapping).

## **Detailed Explanation of `03_post_process.py`**

### **📌 Overview**
This script is responsible for **merging, cleaning, and formatting** processed data into a final structured Excel file. It:
- **Concatenates multiple part files** (`*_part*.csv`).
- **Cleans responses** by removing unwanted text.
- **Combines split records** with the same **Unique ID**.
- **Applies formatting** for readability in Excel.

---

## **🔹 Key Features**
- **Finds and merges part files** into a single final output per court book.
- **Cleans response content** by removing extra bullet points and unwanted lines.
- **Combines related entries** (same `Unique ID`).
- **Formats Excel output** (column widths, text wrapping, tables).
- **Removes unnecessary columns** (`Part`, `EntryDescription`).

---

## **🔎 Step-by-Step Breakdown**

### **1️⃣ Constants & Imports**
```python
OUTPUT_LOCATION = "outputs/"  # Folder containing part files
FILE_PATTERN = "*_part*.csv"  # Pattern to match all part files
```
- Defines the **location** where processed part files are stored.
- Uses a file pattern to **identify part files** (`*_part*.csv`).

---

### **2️⃣ Clean Response Text**
```python
def clean_response(text):
```
- **Removes extra spaces** between bullet points.
- **Deletes unwanted lines** (e.g., `BrewChat`, `XML`, and irrelevant date formats).
- **Adds tab indentation** to each line for better readability.
- **Ensures no leading/trailing whitespace.**

💡 **Why?**  
Prepares LLM responses to be **structured and readable**.

---

### **3️⃣ Format Excel Output**
```python
def format_excel(file_path):
```
- **Freezes the top row** for easier navigation.
- **Auto-adjusts column widths** for better readability.
- **Sets fixed column widths** for key fields:
  - `EntryOriginal`: **30 characters**.
  - `Response`: **100 characters** (to fit combined description + response content).
- **Wraps text** in the `Response` column.
- **Formats the sheet as a table** for better organization.
- **Hides gridlines** to improve visual clarity.

💡 **Why?**  
Ensures the **final Excel output is clear, structured, and easy to read**.

---

### **4️⃣ Merge & Clean Part Files**
```python
def concatenate_parts():
```
- **Finds and groups** all part files (`*_part*.csv`).
- **Sorts files** to process parts in order (`part1`, `part2`, etc.).
- **Concatenates all CSVs** into a single dataframe (`final_df`).
- **Cleans the `Response` column** by combining `EntryDescription` and removing unwanted text.
- **Drops unnecessary columns** (`Part`, `EntryDescription`).
- **Combines related entries** (same `UniqueID`) by:
  - Keeping the **first occurrence** of `EntryDate`, `EntryOriginal`.
  - Merging **all responses** into one structured text.

💡 **Why?**  
Ensures that all **split parts are combined into a single structured record**.

---

### **5️⃣ Save & Apply Formatting**
- **Exports the final cleaned dataset** as an **Excel file (`chronology.xlsx`)**.
- **Applies formatting** using `format_excel()`.
- **Logs the number of processed entries** for reference.

💡 **Why?**  
Finalizes the structured **Excel output**, making it **ready for review and use**.

---

## **🚀 How It Fits Into the Workflow**
✅ **Step 1: Finds and Merges Part Files (`*_part*.csv`)**  
✅ **Step 2: Cleans Responses (Removes Unwanted Text)**  
✅ **Step 3: Combines Entries with the Same Unique ID**  
✅ **Step 4: Saves the Final File (`chronology.xlsx`)**  
✅ **Step 5: Applies Excel Formatting for Readability**  

---

## **🔹 Summary**
| Feature                 | Description |
|------------------------|-------------|
| **Finds Part Files** | Searches for `*_part*.csv` in the output folder |
| **Cleans Response Text** | Removes unwanted bullet points and text |
| **Combines Related Entries** | Merges records with the same `UniqueID` |
| **Formats Excel Output** | Adjusts column widths, wraps text, applies tables |
| **Saves Final Chronology File** | Outputs `chronology.xlsx` per court book |

---


### **4. Cleanup** (`04_cleanup.py`)
- Deletes temporary part files (`*_part*.csv`) from `outputs/`.
## **Detailed Explanation of `04_cleanup.py`**

### **📌 Overview**
This script is responsible for **removing temporary part files** (`*_part*.csv`) from the `outputs/` folder after processing is complete. It ensures the workspace remains clean by deleting unnecessary intermediary files.

---

## **🔹 Key Features**
- **Searches for part files** (`*_part*.csv`).
- **Deletes each matching file** from the output directory.
- **Logs actions** to track deletions and any issues encountered.

---

## **🔎 Step-by-Step Breakdown**

### **1️⃣ Constants & Imports**
```python
OUTPUT_LOCATION = "outputs/"  # Folder containing the CSV files
FILE_PATTERN = "*_part*.csv"  # Pattern to match part files
```
- Defines the **location** where processed part files are stored.
- Uses a file pattern to **identify part files** (`*_part*.csv`).

---

### **2️⃣ Logging Configuration**
```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
```
- **Configures logging** to track deleted files and errors.
- **Logs timestamps, severity levels, and messages**.

---

### **3️⃣ Cleanup Function**
```python
def cleanup_part_files():
```
- **Finds all part files** using `glob.glob()`.
- **Checks if there are any matching files**:
  ```python
  if not part_files:
      logging.info("No part files found for deletion.")
      return
  ```
  If none are found, it logs a message and exits.
- **Attempts to delete each file**:
  ```python
  for file in part_files:
      try:
          os.remove(file)
          logging.info(f"Deleted: {file}")
      except Exception as e:
          logging.error(f"Error deleting {file}: {e}")
  ```
  - **Deletes the file using `os.remove()`**.
  - **Logs the successful deletion**.
  - **Handles errors gracefully**, logging any issues encountered.

💡 **Why?**  
Ensures the workspace stays **clean and organized** by removing unnecessary part files.

---

### **4️⃣ Script Execution**
```python
if __name__ == "__main__":
    cleanup_part_files()
```
- Runs `cleanup_part_files()` **only if the script is executed directly**.
- **Prevents accidental execution** if imported elsewhere.

---

## **🚀 How It Fits Into the Workflow**
✅ **Step 1: Searches for Part Files (`*_part*.csv`)**  
✅ **Step 2: Logs Any Missing Files**  
✅ **Step 3: Deletes Each Matching File**  
✅ **Step 4: Logs Each Deletion**  

---

## **🔹 Summary**
| Feature                 | Description |
|------------------------|-------------|
| **Finds Part Files** | Searches for `*_part*.csv` in the output folder |
| **Deletes Files** | Removes temporary part files to clean up workspace |
| **Logs Actions** | Tracks deletions and any errors encountered |

---

## **✅ Final Steps**
Now that **`04_cleanup.py`** removes unnecessary part files, the entire workflow is **complete**. The final structured **Excel outputs** (`*_chronology.xlsx`) remain, while all intermediate files are cleaned up.

## Usage
### **Run the Scripts Sequentially**
1. Extract data:
   ```sh
   python 01_webapp_extract_data.py
   ```
2. Process extracted data:
   ```sh
   python 02_chronology_generate.py
   ```
3. Post-process and clean:
   ```sh
   python 03_post_process.py
   ```
4. Cleanup temporary files:
   ```sh
   python 04_cleanup.py
   ```

## Logs & Debugging
- **`debug.log`**: Stores logs for debugging.
- Each script prints progress to the console.

## Contributing
If you’d like to improve or extend this project:
1. Fork the repository.
2. Create a new branch.
3. Submit a pull request.

