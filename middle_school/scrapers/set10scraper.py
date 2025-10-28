import requests
import pdfplumber
import csv
import os
import re 

pdf_urls = [
    "https://science.osti.gov/-/media/wdts/nsb/pdf/MS-Sample-Questions/Sample-Set-10/1A_MS_Reg_2016.pdf",
    "https://science.osti.gov/-/media/wdts/nsb/pdf/MS-Sample-Questions/Sample-Set-10/2A_MS_Reg_2016.pdf",
    "https://science.osti.gov/-/media/wdts/nsb/pdf/MS-Sample-Questions/Sample-Set-10/3A_MS_Reg_2016.pdf",
    "https://science.osti.gov/-/media/wdts/nsb/pdf/MS-Sample-Questions/Sample-Set-10/4A_MS_Reg_2016.pdf",
    "https://science.osti.gov/-/media/wdts/nsb/pdf/MS-Sample-Questions/Sample-Set-10/5A_MS_Reg_2016.pdf",
    "https://science.osti.gov/-/media/wdts/nsb/pdf/MS-Sample-Questions/Sample-Set-10/6A_MS_Reg_2016.pdf",
    "https://science.osti.gov/-/media/wdts/nsb/pdf/MS-Sample-Questions/Sample-Set-10/7A_MS_Reg_2016.pdf",
    "https://science.osti.gov/-/media/wdts/nsb/pdf/MS-Sample-Questions/Sample-Set-10/8A_MS_Reg_2016.pdf",
    "https://science.osti.gov/-/media/wdts/nsb/pdf/MS-Sample-Questions/Sample-Set-10/9A_MS_Reg_2016.pdf",
    "https://science.osti.gov/-/media/wdts/nsb/pdf/MS-Sample-Questions/Sample-Set-10/10A_MS_Reg_2016.pdf",
    "https://science.osti.gov/-/media/wdts/nsb/pdf/MS-Sample-Questions/Sample-Set-10/11A_MS_Reg_2016.pdf",
    "https://science.osti.gov/-/media/wdts/nsb/pdf/MS-Sample-Questions/Sample-Set-10/12A_MS_Reg_2016.pdf",
    "https://science.osti.gov/-/media/wdts/nsb/pdf/MS-Sample-Questions/Sample-Set-10/13A_MS_Reg_2016.pdf",
    "https://science.osti.gov/-/media/wdts/nsb/pdf/MS-Sample-Questions/Sample-Set-10/14A_MS_Reg_2016.pdf",
    "https://science.osti.gov/-/media/wdts/nsb/pdf/MS-Sample-Questions/Sample-Set-10/15A_MS_Reg_2016.pdf",
    "https://science.osti.gov/-/media/wdts/nsb/pdf/MS-Sample-Questions/Sample-Set-10/16A_MS_Reg_2016.pdf",
    "https://science.osti.gov/-/media/wdts/nsb/pdf/MS-Sample-Questions/Sample-Set-10/17A_MS_Reg_2016.pdf"
]

def download_pdf(url, path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' 
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/116.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'https://science.osti.gov/',  # optional, can pretend coming from site root
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    with open(path, 'wb') as f:
        f.write(r.content)

def extract_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def cleanUnwanted(text):
    # Removes page and round notes like "High School Round X Page Y" anywhere in the string.
    return re.sub(r'High School Round\s*\d+\s*Page\s*\d+'r'|'r'\d{4}[\s\u00A0]+National Science Bowl(?:\u00AE|\N{REGISTERED SIGN})?[\s\u00A0]*[-–—][\s\u00A0]*Middle School Regional Events[\s\u00A0]+Page[\s\u00A0]+(\d+)(?:["\u201D\u2033])?$', '', text, flags=re.IGNORECASE).strip()
        #LOOK CAREFULLY -- EXAMINE THE UNWANTED PAGE FOOTERS AND PUT THAT SAME EXPRESSION HERE

def parse_questions(text):
    pattern = r'(TOSS-UP|BONUS)\s+.*?(.*?)ANSWER:\s*(.*?)(?=(?:TOSS-UP|BONUS|$))'
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    questions = []
    for qtype, question_text, answer in matches:
        qtype_norm = qtype.lower()
        # SUBJECT
        subject_match = re.search(r'(BIOLOGY|CHEMISTRY|PHYSICS|ENERGY|EARTH SCIENCE|MATH)', question_text, re.IGNORECASE)
        subject = subject_match.group(1).lower() if subject_match else None
        # QUESTION FORMAT
        format_match = re.search(r'(Short Answer|Multiple Choice)', question_text, re.IGNORECASE)
        q_format = format_match.group(1) if format_match else None

        # REMOVE: number, subject and question format from question (redundant)
        prefix_pattern = r'^\s*\d+\)\s*' + (subject if subject else '') + r'\s*' + (q_format if q_format else '') 
        question_clean = re.sub(prefix_pattern, '', question_text, flags=re.IGNORECASE).strip()
        question_clean = ' '.join(question_clean.split())
        
        # Remove spurious header/footer from answer
        answer_clean = cleanUnwanted(answer.strip())

        questions.append({
            'type': qtype_norm,
            'subject': subject,
            'format': q_format,
            'question': question_clean,
            'answer': answer_clean
        })
    return questions



def write_csv(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ["type", "subject", "format", "question", "answer"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

# loop thru pdfs
for i, url in enumerate(pdf_urls, 1):
    local_pdf = f"round{i}.pdf"
    output_csv = f"middle_school/raw_data/set10round{i}.csv" #CHANGE THE SET NUMBER!!!!!
    print(f"Processing {url}...")
    download_pdf(url, local_pdf)
    pdf_text = extract_text(local_pdf)
    questions = parse_questions(pdf_text)
    write_csv(questions, output_csv)
    print(f"Saved {len(questions)} questions to {output_csv}")

print("Processing complete.")
