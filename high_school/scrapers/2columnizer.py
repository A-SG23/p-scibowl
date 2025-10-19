import requests
import pdfplumber
import csv
import os
import re #regex for parsing logic
import pandas as pd
import glob

# big cleaned CSV file
df = pd.read_csv('high_school/cleaned_data/all_rounds_clean.csv')

def clean_question_text(question):
    # remove leading numbers like "1) " from question text
    return re.sub(r'^\d+\)\s*', '', question).strip()

# input prompt using "subject" and "format" 
def create_prompt(row):
    subject = str(row['subject']).capitalize() if pd.notna(row['subject']) else "Unknown"
    qformat = str(row['format']).lower() if pd.notna(row['format']) else "question"
    return f"Generate a {subject} {qformat} question:"


#  cleaning and prompt creation
df['text'] = df.apply(create_prompt, axis=1)
df['target'] = df['question'].apply(clean_question_text)

# select only the two columns needed for fine-tuning
output_df = df[['text', 'target']]

# write the 2-column csv file to the cleaned data folder
output_df.to_csv('high_school/cleaned_data/fine_tune_dataset.csv', index=False)

print(f"Created fine-tuning dataset with {len(output_df)} rows at 'fine_tune_dataset.csv'")
