from openai import OpenAI
import re
import requests
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import pandas as pd
import os
api_key = ''
sender_email = ''
sender_password = ''
resume = f""" """

def read_excluded_companies(filepath='excluded_companies.txt'):
    """Read excluded companies from a file and return as a set."""
    with open(filepath, 'r') as file:
        companies = {line.strip().lower() for line in file}
    return companies
  
def refine_prompt_with_exclusions(prompt_template, exclusion_set):
    """Refine the OpenAI prompt by including excluded company names."""
    exclusion_list = ', '.join(exclusion_set)
    exclusion_clause = f"\nDo not include the following companies: {exclusion_list}."
    return prompt_template + exclusion_clause

def add_company_to_excluded_list(company_name, filepath='excluded_companies.txt'):
    """Append a company name to the exclusion list if not already present."""
    # Normalize the company name for consistent comparison
    company_name = company_name.strip().lower()

    # Read current contents of the file
    with open(filepath, 'r') as file:
        existing_companies = {line.strip().lower() for line in file}

    # Check if the company is already in the exclusion list
    if company_name not in existing_companies:
        with open(filepath, 'a') as file:
            file.write(f"{company_name}\n")
            print(f"Added '{company_name}' to exclusion list.")
    else:
        print(f"'{company_name}' is already in the exclusion list.")

def get_completion(messages, model="gpt-4"):
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content

def extract_companies(response):
    # Define a pattern to extract company information
    company_pattern = r'\d+\.\s*([^\-]+?)\s*-\s*(\S+)'
    matches = re.findall(company_pattern, response)

    # Convert matches to a dictionary
    companies = {name.strip(): domain.strip() for name, domain in matches}
    return companies
def hunter_domain_search(domain, api_key, role='senior, executive'):
    """
    Search Hunter.io for email addresses associated with a specific domain.
    :param domain: The domain to search for.
    :param api_key: Your Hunter.io API key.
    :param role: Role filter.
    :return: List of emails found.
    """
    url = f'https://api.hunter.io/v2/domain-search?domain={domain}&api_key={api_key}&seniority={role}'
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get('data', {}).get('emails', [])
        return results
    else:
        print(f'Error: {response.status_code}, {response.text}')
        return []

def extract_emails(names, domains, api_key, role='senior, executive'):
    """
    Extract email addresses from a list of domains.
    :param domains: List of domains to search.
    :param api_key: Hunter.io API key.
    :param role: Role filter.
    :return: DataFrame of emails.
    """
    all_emails = []
    i = 0
    for domain in domains:
        print(f'Fetching emails for domain: {domain}')
        emails = hunter_domain_search(domain, api_key, role)
        for email in emails:
            all_emails.append({
                'Domain': domain,
                'Email': email['value'],
                'First Name': email['first_name'],
                'Last Name': email['last_name'],
                'Position': email['position'],
                'Confidence': email['confidence'],
                'Type': email['type'],
                'Organization': names[i]
            })
        i += 1

    return all_emails
def create_email(fname, lname, position, companyname, resume):
  messages = [  
    {
        'role': 'system',
        'content': (
            "You are an expert in writing highly persuasive and personalized job-seeking emails. "
            "Your goal is to help candidates secure positions by writing emails to senior people in companies. "
            "Craft emails that are concise, polite, and directly address the needs of the recipient. "
            "Always position the candidate as a strong applicant based on their resume."
        )
    },
    {
        'role': 'user',
        'content': f"""Write a personalized email to {fname} {lname}, who is the {position} at {companyname}. 
        The email should emphasize my strengths in software development, machine learning, or data science roles that align with the company. 
        Use my resume as a reference. Present me as a strong candidate with relevant skills. The subject of the email should be simple, something like looking for opportunites at {companyname}.
        Mention in the email that my resume and work sample has been attached for your reference.
        Here's my resume, delimited by triple backticks:
        ```
        {resume}
        ```
        """
    }
  ]
  email_response = get_completion(messages)
  return email_response

def extract_subject_and_body(email_text):
    # Extract the subject line using regular expressions
    subject_match = re.search(r"^Subject: (.+)$", email_text, re.MULTILINE)
    subject = subject_match.group(1) if subject_match else "No Subject"

    # Remove the subject line from the email text to get the body
    body = re.sub(r"^Subject: .+\n", '', email_text, 1, flags=re.MULTILINE).strip()
    
    return subject, body

def send_email_with_attachment(recipient_email, subject, company_name, message_body, sender_email, sender_password, attachment_paths=None):
    """
    Send an email via SMTP with optional attachments.
    :param recipient_email: Recipient's email address.
    :param subject: Subject of the email.
    :param message_body: Body of the email.
    :param sender_email: Sender's email address.
    :param sender_password: Sender's email password.
    :param attachment_paths: List of paths to the files to attach.
    """
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message_body, 'plain'))

    # Attach files if any
    if attachment_paths:
        for path in attachment_paths:
            try:
                with open(path, 'rb') as file:
                    part = MIMEApplication(file.read(), Name=os.path.basename(path))
                    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(path)}"'
                    msg.attach(part)
            except Exception as e:
                print(f'Could not attach file {path}: {e}')

    try:
        # Initialize SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        print(f'Successfully sent email to {recipient_email}')
    except Exception as e:
        print(f'Failed to send email to {recipient_email}: {e}')

client = OpenAI()
prompt_template = f"""
You are an experienced career advisor specializing in software development and data science roles. Assume you're helping a recent computer science graduate find job opportunities. Your task is to suggest 10 small and mid-sized companies where jobs in entry-level software development or machine learning roles are available. Please refine the list to only include companies based in the United States. Provide their domain addresses.
Print the output in the following format:
1. Company name 1 - domain address 1
2. Company name 2 - domain address 2
"""
excluded_companies = read_excluded_companies()
prompt = refine_prompt_with_exclusions(prompt_template, excluded_companies)
messages = [{"role": "user", "content": prompt}]
response = get_completion(messages)
print(response)
companies = extract_companies(response)
company_domains = []
company_names = []
for key, value in companies.items():
  company_names.append(key)
  company_domains.append(value)
email_df = extract_emails(company_names, company_domains, api_key)
attachment_paths = []
counter = 0
for emails in email_df:
    email_to_send = create_email(emails['First Name'], emails['Last Name'], emails['Position'], emails['Organization'], resume)
    print(emails['First Name'], emails['Last Name'], emails['Position'], emails['Organization'], emails['Domain'])
    subject, body = extract_subject_and_body(email_to_send)
    send_email_with_attachment(emails['Email'], subject, emails['Organization'], body, sender_email, sender_password, attachment_paths)
    add_company_to_excluded_list(emails['Organization'])
    print("Email sent to company ", counter+1)
    counter += 1