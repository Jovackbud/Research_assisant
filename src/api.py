from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import logging
import re
import json
import pandas as pd
from pathlib import Path
import tempfile
import os # Ensure os is imported for file operations
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ValidationError

# Imports for unique file naming and finding the latest file
import uuid
from datetime import datetime
import glob # Used in download_csv to find files

# Ensure docx is imported if extract_text_from_docx is defined here or if it's used elsewhere.
# However, since it's moved to utils, it's only needed if utils needs it.
# For safety, and if utils were to use it directly, keep it. If utils does not, it could be removed.
# For now, keeping it as it was in the original api.py.
import docx

from src.reviewer import review
from src.utils import extract_text_from_pdf, extract_text_from_docx, save_dataframe_to_csv # Updated import

# --- Pydantic Model Definition ---
class ResearchPaperData(BaseModel):
    title_of_paper: Optional[str] = None
    author: Optional[str] = None
    year_of_publication: Optional[str] = None
    country_of_publication: Optional[str] = None
    research_objective: Optional[str] = None
    independent_variable_or_cause: Optional[str] = None
    dependent_variable_or_effect: Optional[str] = None
    estimation_techniques: Optional[str] = None
    theory: Optional[str] = None
    methods: Optional[str] = None
    findings: Optional[str] = None
    recommendations: Optional[str] = None
    research_gap: Optional[str] = None
    references: Optional[str] = None
    remarks: Optional[str] = None

# --- FastAPI App Setup ---

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse # Already imported, but confirming
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Serve static files from the 'static' directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html at root
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serves the index.html file from the static directory."""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logging.error("static/index.html not found.")
        return "<h1>Research Assistant</h1><p>Error: index.html not found in static/. Please ensure it exists.</p>"
    except Exception as e:
        logging.error(f"Error reading index.html: {e}")
        return f"<h1>Research Assistant</h1><p>An error occurred while loading the page.</p>"


# Load configuration from config.json
def load_config(config_path='config.json'):
    """Load configuration from a JSON file."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        logging.error(f"Configuration file not found at {config_path}. Using default settings.")
        # Define sensible defaults if config file is missing
        return {"input_folder": "data/papers", "output_csv": "data/response/uploaded_files_result.csv", "log_file": "api.log"}
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from {config_path}. Please check the file format. Using default settings.")
        return {"input_folder": "data/papers", "output_csv": "data/response/uploaded_files_result.csv", "log_file": "api.log"}
    except Exception as e:
        logging.error(f"Failed to load config file {config_path}: {e}. Using default settings.")
        return {"input_folder": "data/papers", "output_csv": "data/response/uploaded_files_result.csv", "log_file": "api.log"}

config = load_config()

# Setup logging
log_file_path = config.get('log_file', 'api.log')
# Ensure log directory exists if specified in config
log_dir = os.path.dirname(log_file_path)
if log_dir and not os.path.exists(log_dir):
    try:
        os.makedirs(log_dir, exist_ok=True)
    except OSError as e:
        print(f"Warning: Could not create log directory '{log_dir}': {e}. Logs will be written to the current directory.")
        log_file_path = 'api.log' # Fallback if directory creation fails

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(), # Log to console
        logging.FileHandler(log_file_path) # Log to file
    ]
)

# --- API Endpoints ---
@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    """Handles file uploads, processes them with the AI review, and returns results."""
    processed_data = []
    failed_files_list = []
    # Use the base path from config to create unique filenames
    output_csv_base_path = config.get('output_csv', 'data/response/uploaded_files_result.csv')

    # Track the filename generated for this batch
    generated_csv_filename = None 

    for file in files:
        temp_file_path = None
        try:
            filename = file.filename or ""
            file_extension = Path(filename).suffix.lower()
            
            # Create a temporary file to store uploaded content.
            # delete=False means we are responsible for cleaning it up.
            # Using prefix from stem to better identify temp files related to original name.
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension, prefix=f"{Path(filename).stem}_", dir=tempfile.gettempdir()) as tmp_file:
                tmp_file.write(await file.read())
                tmp_file_path = tmp_file.name

            logging.info(f"Processing file: {file.filename} (Temp path: {tmp_file_path})")
            text = ""
            if file_extension == ".pdf":
                text = extract_text_from_pdf(tmp_file_path)
            elif file_extension == ".docx":
                text = extract_text_from_docx(tmp_file_path)
            else:
                logging.warning(f"Unsupported file type: {file.filename}. Skipping.")
                failed_files_list.append(f"{file.filename} (Unsupported type)")
                continue

            if not text or not text.strip(): # Check if text is empty or only whitespace
                logging.warning(f"No text extracted from {file.filename}. Skipping review.")
                failed_files_list.append(f"{file.filename} (No text extracted)")
                continue

            # Call the review function which interacts with the AI model
            ai_response_text = review(text)

            if not ai_response_text: # Handle cases where review() returns empty string (e.g., API key missing)
                logging.warning(f"AI review returned empty response for {file.filename}.")
                failed_files_list.append(f"{file.filename} (AI review failed)")
                continue

            try:
                # Clean up potential markdown wrappers and parse as JSON
                cleaned_response = ai_response_text.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:]
                    if cleaned_response.endswith("```"):
                        cleaned_response = cleaned_response[:-3]
                elif cleaned_response.startswith("```"): # Handle cases where it's just code block
                    cleaned_response = cleaned_response[3:]
                    if cleaned_response.endswith("```"):
                        cleaned_response = cleaned_response[:-3]
                
                parsed_json_data = json.loads(cleaned_response)
                # Validate the parsed data against the Pydantic model
                validated_data = ResearchPaperData(**parsed_json_data)
                processed_data.append(validated_data.dict())
                logging.info(f"Successfully processed and validated: {file.filename}")

            except json.JSONDecodeError:
                logging.warning(f"JSON Decode Error for {file.filename}. Response was: '{ai_response_text[:200]}...'")
                failed_files_list.append(f"{file.filename} (Invalid JSON format)")
            except ValidationError as ve:
                logging.warning(f"Pydantic Validation Error for {file.filename}: {ve.errors()}. Response was: '{ai_response_text[:200]}...'")
                failed_files_list.append(f"{file.filename} (Data validation failed)")
            except Exception as e:
                logging.error(f"Unexpected error processing AI response for {file.filename}: {e}")
                failed_files_list.append(f"{file.filename} (Processing error)")

        except ImportError as ie:
            logging.error(f"Import Error processing {file.filename}: {ie}")
            failed_files_list.append(f"{file.filename} (Dependency error: {ie})")
        except Exception as e:
            logging.error(f"General error processing file {file.filename}: {e}")
            failed_files_list.append(f"{file.filename} (General error: {e})")
        finally:
            # Crucially, delete the temporary file to ensure statelessness
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    logging.debug(f"Cleaned up temporary file: {temp_file_path}")
                except OSError as e:
                    logging.error(f"Error removing temporary file {temp_file_path}: {e}")

    # Save results to CSV if any data was processed
    csv_was_generated = False
    
    if processed_data:
        df = pd.DataFrame(processed_data)
        try:
            # Generate a unique filename with timestamp and UUID for this batch
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = uuid.uuid4()
            # This is the filename we will return to the frontend
            generated_csv_filename = f"review_results_{timestamp_str}_{unique_id}.csv"

            # Ensure the output directory exists using the base path from config
            output_dir = os.path.dirname(output_csv_base_path)
            os.makedirs(output_dir, exist_ok=True) # Ensure directory exists

            # Construct the full path for this specific CSV file
            current_output_csv_path = os.path.join(output_dir, generated_csv_filename)

            # Save the dataframe to the uniquely named CSV file
            save_dataframe_to_csv(df, current_output_csv_path)
            logging.info(f"Saved results for {len(processed_data)} files to {current_output_csv_path}")
            csv_was_generated = True # Mark that a CSV has been created for this batch

        except Exception as e:
            logging.error(f"Failed to save CSV: {e}")
            # Reset filename if saving fails, so it's not returned as generated
            generated_csv_filename = None 
    else:
        logging.warning("No data processed successfully to save.")

    # Return status including whether CSV was generated for this batch and its filename
    return JSONResponse({
        "total_files_uploaded": len(files),
        "files_processed_successfully": len(processed_data),
        "files_failed_or_skipped": len(failed_files_list),
        "failed_files_details": failed_files_list,
        "results_preview": processed_data[:5], # Show a preview of successful results
        "csv_generated": csv_was_generated, # Indicate if a CSV was saved for this batch
        "generated_csv_filename": generated_csv_filename # <-- New: return the filename of the saved CSV
    })

# MODIFIED Endpoint to download a SPECIFIC generated CSV file
# The route now accepts a filename parameter.
@app.get("/download/csv/{filename}") 
async def download_specific_csv(filename: str): # Added filename parameter
    """
    Serves a SPECIFIC generated CSV file for download, identified by its filename.
    Ensures the requested file is within the designated output directory and matches the naming convention.
    """
    # Get the directory path from the config, using a default if not specified
    output_dir = os.path.dirname(config.get('output_csv', 'data/response/uploaded_files_result.csv'))
    
    # Construct the full path to the requested file
    requested_csv_path = os.path.join(output_dir, filename)

    # --- Security Check ---
    # Ensure the requested file is within the expected output directory and matches the naming convention.
    # This prevents malicious users from requesting arbitrary files on the server (directory traversal).
    
    # Get the absolute path of the output directory to prevent going up the tree
    abs_output_dir = os.path.abspath(output_dir)
    # Get the absolute path of the requested file
    abs_requested_csv_path = os.path.abspath(requested_csv_path)

    # 1. Check if the absolute path of the requested file starts with the absolute path of the output directory.
    # 2. Check if the filename follows our expected pattern (starts with "review_results_" and ends with ".csv").
    #    A more robust check could use regex for the entire filename pattern.
    if not abs_requested_csv_path.startswith(abs_output_dir) or \
       not filename.startswith("review_results_") or \
       not filename.endswith(".csv"):
        
        logging.warning(f"Attempted to access invalid or disallowed file: {filename} from {abs_requested_csv_path}")
        return JSONResponse({"detail": "Invalid filename or path requested."}, status_code=400)

    # Check if the file actually exists at the constructed path
    if not os.path.exists(requested_csv_path):
        logging.warning(f"Requested CSV file not found: {requested_csv_path}")
        return JSONResponse({"detail": f"CSV file '{filename}' not found. It might have been deleted or never created."}, status_code=404)

    try:
        logging.info(f"Serving specific CSV file for download: {requested_csv_path}")
        # Serve the requested CSV file using FileResponse
        return FileResponse(
            path=requested_csv_path,
            filename=os.path.basename(requested_csv_path), # Suggests a filename for download
            media_type='text/csv'
        )
    except Exception as e:
        logging.error(f"Error serving CSV file {requested_csv_path}: {e}")
        return JSONResponse({"detail": "An error occurred while serving the CSV file."}, status_code=500)