CTP Chronology Extractor

Overview

The CTP Chronology Extractor is a Python-based tool designed to extract medical events and associated dates from provided documents. The system processes input files, extracts relevant data, and structures it in a chronological format. It is optimized for accuracy and consistency using an iterative LLaMA-based prompt refinement approach.

Features

Medical Event Extraction: Identifies medical events and their corresponding dates.

Structured Output: Formats extracted data as [DATE] - [EVENT].

LLaMA-Based Prompt Optimization: Uses an AI-driven approach to refine prompts for improved accuracy.

Courtbook Handling: Processes courtbook documents for relevant data extraction.

Logging & Tracking: Maintains logs of runs and extracted data.

File Structure

CTP_chronology/
│── __pycache__/               # Compiled Python cache files
│── .env                       # Environment variables (credentials, config)
│── .gitignore                 # Git ignore rules
│── 00_courtbooks_to_get.csv   # List of courtbooks for processing
│── 01_fss_extract.py          # Extracts FSS (Forensic Science Services) data
│── 02_chronology_generate.py  # Generates chronological records
│── 11616_chronology.csv       # Output file with extracted chronology
│── 11616_courtbook.csv        # Courtbook data file
│── llm_class.py               # LLM client handling AI-based extraction
│── prompt_list.csv            # List of tested prompts for optimization
│── README.md                  # Project documentation
│── run_logs.csv               # Log file tracking extraction runs
│── windows_run_scripts.bat    # Windows batch script for running the process

Installation

Prerequisites

Ensure you have the following installed:

Python 3.8+

pip (Python package manager)

virtualenv (recommended for environment isolation)

Setup

Clone the repository:

git clone https://github.com/your-repo/CTP_chronology.git
cd CTP_chronology

Set up a virtual environment (optional but recommended):

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Set up environment variables:

Create a .env file in the root directory with the following:

USERNAME=your_username
EMAIL=your_email@example.com
PASSWORD=your_password

Usage

Extract Medical Chronology

Run the extraction process:

python 01_fss_extract.py

To generate the chronology:

python 02_chronology_generate.py

Running on Windows

Use the provided batch script:

windows_run_scripts.bat

Output Format

The extracted chronology is stored in 11616_chronology.csv with the format:

[DATE] - [EVENT]

Example output:

2024-05-12 - Fractured wrist diagnosed
2023-09 - Surgery for ligament tear
2021 - Initial injury reported

Prompt Optimization Process


Prompts are stored in prompt_list.csv

The optimized LLM model is handled via llm_class.py

Run logs are saved in run_logs.csv for review

Notes & Limitations

The system does not extract dates from document headers or letterheads.

Uncertain or ambiguous dates (e.g., medication dosages mistaken for dates) are not included.

If a specific day is unavailable, the system uses month & year or just the year.

License

This project is licensed under MIT License.

