import pdfplumber
import glob
import os
import pandas as pd
import logging
import docx

# Configure logging for utils if needed, or rely on main logger
# logging.basicConfig(level=logging.INFO)

def get_pdf_files(directory):
    """
    Retrieves all PDF files from the specified directory.
    """
    return glob.glob(os.path.join(directory, '*.pdf'))

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ''.join(page.extract_text() for page in pdf.pages if page.extract_text())
        return text
    except Exception as e:
        # Use logging instead of print for errors
        logging.error(f"Error extracting text from {pdf_path}: {e}")
        return ""

def extract_text_from_docx(docx_path_or_file_obj):
    """Extracts text from a docx file path or file object."""
    if not docx:
        raise ImportError("python-docx is not installed. Please install it to process Word files.")
    try:
        document = docx.Document(docx_path_or_file_obj)
        return '\n'.join([para.text for para in document.paragraphs])
    except Exception as e:
        logging.error(f"Failed to extract text from docx: {e}")
        return ""

def save_dataframe_to_csv(df, output_path='data/review/output.csv'):
    """
    Saves the DataFrame to a CSV file.
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        df.to_csv(output_path, index=False)
        logging.info(f"Saved results to {output_path}")
    except Exception as e:
        logging.error(f"Failed to save CSV to {output_path}: {e}")