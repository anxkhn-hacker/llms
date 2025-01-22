import json
import re

import requests
from ollama import chat

# open companies.txt and load them into a list

companies = [
    "https://7eleven.wd3.myworkdayjobs.com/7eleven",
    "https://aaaie.wd1.myworkdayjobs.com/CSAACareers",
    "https://aaamidatlantic.wd5.myworkdayjobs.com/AAAMidAtlantic",
    "https://aamc.wd5.myworkdayjobs.com/AAMC",
    "https://abbott.wd5.myworkdayjobs.com/abbottcareers",
]

models = [
    "smollm2",
    "smollm2:360m",
    "smollm2:135m",
    "llama3.2",
    "llama3.2:1b",
    "qwen2.5:3b",
    "qwen2.5:1.5b",
    "qwen2.5:0.5b",
    "hermes3:3b",
    "phi3.5",
    "gemma2:2b",
    "internlm2:1.8b",
    "deepseek-r1:1.5b",
]

with open("companies-smol.txt", "r") as file:
    companies = file.readlines()

for company in companies:
    company_url = company.strip()

    for model in models:

        # send curl request to the company's careers page
        # and get the response
        pattern = r"https://([^.]+)\.(wd\d+)\.myworkdayjobs\.com/([^/]+)"
        replacement = r"https://\1.\2.myworkdayjobs.com/wday/cxs/\1/\3"
        internal_url = re.sub(pattern, replacement, company_url)
        print(company_url)

        # add /approot to the url
        approot_url = internal_url + "/approot"
        sidebar_url = internal_url + "/sidebar"

        response1 = requests.get(approot_url)
        response2 = requests.get(sidebar_url)

        mixed_content = response1.text + response2.text
        # print(mixed_content)
        response = chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": f"Extract and provide only the main company name and the company's main URL (avoid LinkedIn, careers pages, Workday, or similar recruitment-related pages). Prioritize extracting the URL from sources such as the company's homepage, privacy policy page, or other official web pages. If no explicit URL is found, predict the main company website based on the context of the job description. Do not include location, country, or any other additional details. Use the following job description for your analysis: {mixed_content}",
                }
            ],
            format={
                "type": "object",
                "properties": {
                    "company_name": {"type": "string"},
                    "company_url": {"type": "string"},
                },
                "required": ["company_name", "company_url"],
            },
        )

        response_content1 = json.loads(response["message"]["content"])
        print(
            "From homepage:",
            response_content1.get("company_name"),
            response_content1.get("company_url"),
        )

        # get the company name and url from the job description
        jobs_link = internal_url + "/jobs"
        body = {"limit": 20, "offset": 0, "searchText": ""}

        post_responce = requests.post(jobs_link, json=body)
        # load the json response into a dictionary
        job_data = json.loads(post_responce.text)
        job_link = job_data.get("jobPostings")[0].get("externalPath")

        job_responce = requests.get(internal_url + job_link)

        response = chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": f"Extract and provide only the main company name and the company's main URL (avoid LinkedIn, careers pages, Workday, or similar recruitment-related pages). Prioritize extracting the URL from sources such as the company's homepage, privacy policy page, or other official web pages. If no explicit URL is found, predict the main company website based on the context of the job description. Also, analyze the job description to determine the most logical minimum and maximum salary for the role based on company, location, job title, experience required, and industry standards. Provide this information in the local currency. Do not include location, country, or any other additional details. Use the following job description for your analysis: {job_responce.text}",
                }
            ],
            format={
                "type": "object",
                "properties": {
                    "company_name": {"type": "string"},
                    "company_url": {"type": "string"},
                    "salary_min": {"type": "number"},
                    "salary_max": {"type": "number"},
                    "currency": {"type": "string"},
                },
                "required": [
                    "company_name",
                    "company_url",
                    "salary_min",
                    "salary_max",
                    "currency",
                ],
            },
        )

        response_content2 = json.loads(response["message"]["content"])
        print(
            "From job:",
            response_content2.get("company_name"),
            response_content2.get("company_url"),
        )

        # save the company url, company name and job description in a file
with open("companies-smol.txt", "a") as file:
    file.write(
        f"{company_url},{response_content1.get('company_name')},{response_content1.get('company_url')},{response_content2.get('company_name')},{response_content2.get('company_url')},{response_content2.get('salary_min')},{response_content2.get('salary_max')},{response_content2.get('currency')},{model}\n"
    )
