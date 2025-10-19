import pandas as pd

df = pd.read_csv('high_school/cleaned_data/high_school_all.csv')
# Remove duplicates
df = df.drop_duplicates()
# Standardize column format
df['subject'] = df['subject'].str.strip().str.lower() #standardize everything by making lowercase
df['format'] = df['format'].str.strip().str.title() #Title Case
df['type'] = df['type'].str.strip().str.lower() #lowercase

# Remove questions/answers with odd length
#df = df[df['question'].str.len() > 15]

# Example: validate 'subject' has the 6 allowed categories only. this filters out anything without these labels
allowed_subjects = {'biology', 'chemistry', 'physics', 'energy', 'earth science', 'math'}

df = df[df['subject'].isin(allowed_subjects)]

# Example: Remove rows with empty question or answer fields, if not extracted in a useful way
df = df[df['question'].str.strip() != '']
df = df[df['answer'].str.strip() != '']

# Save cleaned version
df.to_csv('high_school/cleaned_data/all_rounds_clean.csv', index=False)
