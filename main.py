import re
import ast
from src.reviewer import review
from src.utils import get_pdf_files, extract_text_from_pdf, save_dataframe_to_csv
import pandas as pd


def main():
    pdf_input_directory = 'data/papers/13'
    output_csv_file = 'data/response/review13.csv'
    pdf_files = get_pdf_files(pdf_input_directory)
    if not pdf_files:
        print(f"No PDF files found in {pdf_input_directory}. Exiting.")
        return
    pdf_texts = [extract_text_from_pdf(paper) for paper in pdf_files]

    data = []  # List to collect each dictionary
    failed_to_parse_files = []  # List to collect files that failed to parse

    for i in range(len(pdf_files)):
        api_response = review(pdf_texts[i])
        match = re.search(r"\{.*\}", api_response, re.DOTALL)
        if match:
            dictionary_content = match.group(0)
            try:
                response = ast.literal_eval(dictionary_content)
                data.append(response)  # Collect dictionary
            except (SyntaxError, ValueError):
                print(f"Skipping invalid response for file {pdf_files[i]}")
                failed_to_parse_files.append(pdf_files[i])

    # Convert collected data to DataFrame in one go
    if failed_to_parse_files:
        print("\n--- Files that failed to parse ---")
        for filepath in failed_to_parse_files:
            print(filepath)
        print("------------------------------------\n")
    df = pd.DataFrame(data)
    save_dataframe_to_csv(df, output_csv_file)


if __name__ == '__main__':
    main()
    print('Done')
