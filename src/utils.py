import pdfplumber
import glob
import os
import pandas as pd


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
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""


def create_dataframe():
    """
    Creates a DataFrame with column for all needed information.
    """
    df = pd.DataFrame(columns=["title of paper", "author", "year of publication", "country of publication",
                               "research objective", "independent variable or cause", "dependent variable or effect",
                               "estimation techniques", "theory", "methods", "findings", "recommendation(s)",
                               "research gap", "references", "remarks"])
    df.sort_values(by='Score (%)', ascending=False, inplace=True)
    return df


def save_dataframe_to_csv(df, output_path='data/review/output.csv'):
    """
    Saves the DataFrame to a CSV file.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
