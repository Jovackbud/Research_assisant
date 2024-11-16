import re
import ast
from src.reviewer import review
from src.utils import get_pdf_files, extract_text_from_pdf, save_dataframe_to_csv
import pandas as pd


def main():
    pdf_path = 'data/papers/13'
    pdf_files = get_pdf_files(pdf_path)
    pdf_texts = [extract_text_from_pdf(paper) for paper in pdf_files]

    data = []  # List to collect each dictionary

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

    # Convert collected data to DataFrame in one go
    df = pd.DataFrame(data)
    save_dataframe_to_csv(df, "data/response/review13.csv")


if __name__ == '__main__':
    main()
    print('Done')
