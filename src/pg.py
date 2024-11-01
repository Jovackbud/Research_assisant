"""
imports
"""

"""
paper directory
"""

"""
list all papers
"""

"""
extract papers into a table
"""

"""
read and summarize papers into a dictionary respectively
"""

"""
add the dictionary as a new row in a table (data frame) respectively
"""

"""
save the data frame as a csv file
"""

for i in range(len(pdf_files)):
    response = review(pdf_texts[i]).split('python')
    df = pd.concat([df, pd.DataFrame([response])], ignore_index=True)

# df.to_csv('data/review/reviews.csv')
print(df.head())