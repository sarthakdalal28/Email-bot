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
resume = f""" Sarthak Dalal
New Brunswick, NJ | P: +1 (848) 448-9098 | sarthakd2807@gmail.com | LinkedIn |Github| Website
EDUCATION
Rutgers University New Brunswick, NJ 
Master of Science in Computer Science (GPA: 3.9/4.0) Sept 2022 - May 2024
Relevant Coursework: Introduction to AI, Data Structures and Algorithms, Mathematical Foundations of Data Science, 
 Database Systems for Data Science, Machine Learning, Computer Vision 
Dwarkadas J Sanghvi College of Engineering Mumbai, India 
Bachelor of Engineering in Electronics and Telecommunications (CGPA: 8.86/10) Aug 2018 – May 2022
Minors in Artificial Intelligence and Machine Learning
Relevant Coursework: Structured Programming Approach, OOP using Java, Database Management System, Machine Vision, Big Data Analytics 
Certificates: Algorithmic Toolbox (UC San Diego, Coursera) | Bootstrap 4 (The Hong Kong University of Science and Technology, Coursera) | 
 Interactivity with JavaScript (University of Michigan, Coursera) | Programming for Everybody (University of Michigan, Coursera) 
SKILLS
ML Frameworks and Libraries - TensorFlow, Pytorch, scikit-learn, Keras, numpy, Pandas, OpenCV 
Web Technologies: HTML, CSS, Bootstrap, Flask, NodeJS, TypeScript 
Databases: SQL, MongoDB 
Programming Languages: C, C++, R, Java, Python, JavaScript 
 
WORK EXPERIENCE
Rutgers University Sep 2023 – May 2024
Teaching Assistant
● Facilitate weekly recitations for two classes, each comprising 20 students, in CS170: Computer Applications for Business, covering essential 
 topics such as HTML, CSS, JavaScript, Microsoft Excel, and SQL.
● Assess and grade weekly assignments, midterm, and final exams, ensuring timely and constructive feedback for student development.
PipeIQ Jun 2023 – August 2023 
Machine Learning Intern
● Engineered a customer-centric chatbot utilizing prompt engineering and LangChain technologies. The chatbot seamlessly integrates into client 
websites, bolstered by PipeIQ backend, enhancing user interaction.
● Spearheaded the development of a robust FastAPI endpoint to host the PipeIQ backend on AWS Elastic Beanstalk, ensuring optimal 
performance and scalability for the chatbot, resulting in improved user experiences.
● Implemented strategic analytics integration using Google Tag Manager, incorporating Google Analytics, DealFront, and PeopleDataLabs onto 
the PipeIQ website. Leveraged PeopleDataLabs Data and reverse IP lookup to identify and personalize user interactions, a pivotal technology 
now integral to the chatbot's functionality.
Indian Institute of Technology - Delhi Jun 2021 – Apr 2022 
Machine Learning Research Intern
● Investigated the application of Artificial Intelligence and Natural Language Processing in the Indian Judiciary 
System and how AI may be used to augment the judiciary.
● Implemented several summarization models (LexRank, Latent Semantic Analysis, T5, Bart-large-CNN) using Machine Learning and Deep 
Learning to summarize lengthy case documents which were 30% the length of the original documents and compared the results.
PROJECTS
Optimizing Energy Efficiency: A Comprehensive Analysis of Household Electricity Consumption March 2024 – May 2024
● Developed machine learning models to predict household electricity consumption, using time-series analysis to enable data-driven decisions for 
energy savings. Implemented various models including Polynomial Regression, XGBoost, Random Forest, and CatBoost, with Random Forest 
achieving the lowest RMSE.
● Enhanced model insights by integrating findings into a user-friendly interface using the Django framework, facilitating real-time energy 
consumption predictions to promote efficient energy use and cost savings.
Age, Gender and Ethnicity Prediction May 2023
● Developed an image classification system using deep learning techniques to predict age, gender, and ethnicity from uploaded images.
● Trained the models on a labeled dataset containing images representing various age, gender, and ethnicity groups.
● Developed a Flask web application to provide an interactive user interface for image upload and prediction.
● Integrated the trained models into the Flask app, allowing users to upload an image and receive predictions for age, gender, and ethnicity.
BidBazaar Feb 2023 – Apr 2023
● An auction website like eBay, with features like user account creation, auctions, browsing and advanced search functionality, and admin and 
customer representative functions.
Two-Way Real-Time Sign Language Recognition using Convolutional Neural Network Feb 2023 – Apr 2023
● Developed a Two-Way Real-Time Sign Language Recognition system using a Convolutional Neural Network (CNN) for American Sign 
Language (ASL) and Indian Sign Language (ISL).
● Used a dataset with 140 images for each sign for both language systems, used skin detection and hand segmentation techniques to isolate the 
hand region from the background.
● Implemented CNN for classification of signs and achieved an accuracy of over 90% on the test set.
Fast Trajectory Replanning Sep 2022 – Oct 2022
● Led a team of 3 in developing a maze-solving application using the A* search algorithm that enables an agent to navigate a 101x101 grid maze 
with obstacles to reach a target cell using the shortest route, with a Manhattan distance heuristic.
● Implemented and tested backward A* search and adaptive A* search algorithms, comparing their execution times to forward A* search.
● Created an interactive graphical user interface using the pygame module to visually display the shortest path the agent takes to reach the target.
Battery Management and Data Analytics of Battery and Vehicle Data Sep 2021 – Apr 2022
● Led a team of 4 in designing a Data Acquisition System and Battery Management System and integrating
 it into the brain of the vehicle, (Vehicle Control Unit) to create a robust electronics system for an Electrics Vehicle.
● Prepared Machine Learning models such as Gradient Boosting, Random Forest, LASSO Regression to predict 
 the SOC (State of Charge) of the battery of the vehicle. Gradient Boosting achieved the best R2 score of 0.977.
PUBLICATIONS
LexRank and PEGASUS Transformer for Summarization of Legal Documents May 31, 2022
Machine Intelligence and Signal Processing (MISP) 
● The research paper presented a novel method of abstractive summarization of legal documents using LexRank algorithm and PEGASUS 
Transformer.
● The summaries generated by this method outperformed 5 other methods tested on 6 documents by achieving a ROUGE-F1 metric of 0.689.
● Awarded the Best Paper in the presented track at MISP, 2022.
A Comparative Study on Sign Language Recognition Methods Sep 09, 2022
3
rd International Conference on Sustainable Expert Systems (ICSES), IEEE
● The review paper compared different sensor-based and vision-based approaches to Sign Language Recognition using ML.
Arbitrage in Cryptocurrency: A Survey Oct 22, 2021
5
th International Conference on Information Systems and Computer Networks (ISCON), IEEE
● The paper deals with using arbitrage in cryptocurrencies over three exchanges and analyzing the profit created over a particular time frame.
EXTRACURRICULARS
Elected as a low voltage systems engineer for team DJS Racing, a formula student team at Dwarkadas J Sanghvi College of Engineering that 
manufactures Electric formula one type race cars – The team secured Fourth position in Engineering Design Category at Formula Bharat 2021 
and received the Best Powertrain package award at FSEV Concept Challenge 2020. Trained juniors to ensure smooth knowledge transfer."""

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