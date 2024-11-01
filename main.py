import json

from src.reviewer import review
from src.utils import get_pdf_files, extract_text_from_pdf, create_dataframe, save_dataframe_to_csv
import pandas as pd
import re


def main():
    pdf_path = 'data/papers'
    pdf_files = get_pdf_files(pdf_path)
    pdf_texts = [extract_text_from_pdf(paper) for paper in pdf_files]

    df = pd.DataFrame(columns=["Title of Paper", "Author", "Year of Publication", "Country of Publication",
                               "Research Objective", "Independent Variable or Cause", "Dependent variable or Effect",
                               "Estimation Techniques", "Theory", "Methods", "Findings", "Recommendation(s)",
                               "Research Gap", "References", "Remarks"])

    for i in range(len(pdf_files)):
        response = review(pdf_texts[i]).split('python')
        # Extract JSON-like content using regex
        json_data = re.search(r'```json\n(.+)\n```', response[0], re.DOTALL).group(1)
        result = json.loads(json_data)
        df = pd.concat([df, pd.DataFrame([result])], ignore_index=True)

    df.to_csv('data/review/reviews.csv')
    print(df.head())


if __name__ == '__main__':
    main()
    print('Done')
