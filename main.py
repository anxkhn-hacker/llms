import json
import re

import requests
from ollama import chat
import time

# open companies.txt and load them into a list

companies = [
    "https://7eleven.wd3.myworkdayjobs.com/7eleven",
    "https://aaaie.wd1.myworkdayjobs.com/CSAACareers",
    "https://aaamidatlantic.wd5.myworkdayjobs.com/AAAMidAtlantic",
    "https://aamc.wd5.myworkdayjobs.com/AAMC",
    "https://abbott.wd5.myworkdayjobs.com/abbottcareers",
    "https://abeilleassurances.wd3.myworkdayjobs.com/External",
    "https://absa.wd3.myworkdayjobs.com/ABSAcareersite",
    "https://accelya.wd103.myworkdayjobs.com/Careers",
    "https://accenture.wd103.myworkdayjobs.com/AccentureCareers",
    "https://acehardware.wd1.myworkdayjobs.com/External",
    "https://activision.wd1.myworkdayjobs.com/External",
    "https://acxiomllc.wd5.myworkdayjobs.com/AcxiomUSA",
    "https://adobe.wd5.myworkdayjobs.com/external_experienced",
    "https://aes.wd1.myworkdayjobs.com/AES_ANDES",
    "https://aes.wd1.myworkdayjobs.com/AES_US",
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
    "smallthinker",
    "granite3.1-moe",
    "granite3.1-moe:1b",
]

big_models = ["phi4", "llama3.2", "deepseek-r1:8b"]


for model in big_models:
    model = model + "-model"

    for company in companies:
        company_url = company.strip()
        # send curl request to the company's careers page
        # and get the response
        pattern = r"https://([^.]+)\.(wd\d+)\.myworkdayjobs\.com/([^/]+)"
        replacement = r"https://\1.\2.myworkdayjobs.com/wday/cxs/\1/\3"
        internal_url = re.sub(pattern, replacement, company_url)
        print(company_url)

        # get the company name and url from the job description
        jobs_link = internal_url + "/jobs"
        body = {"limit": 20, "offset": 0, "searchText": ""}

        post_responce = requests.post(jobs_link, json=body)
        # load the json response into a dictionary
        job_data = json.loads(post_responce.text)
        job_link = job_data.get("jobPostings")[0].get("externalPath")

        job_responce = requests.get(internal_url + job_link)
        print(internal_url + job_link)

        # start timer here to measure the time taken to get the response
        start_time = time.time()

        response = chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": """Extract and provide the main company name from the job description. Analyze the job description step-by-step to determine the most logical minimum and maximum annual salary for the role based on the company, location, job title, experience required, and industry standards. Follow these steps for salary calculation:

                    Carefully analyze the salary information provided in the job description.
                    Consider the type of employment specified: full-time, part-time, contract, internship, etc.
                    If the salary is given as a weekly rate:
                    Multiply it by 40 hours per week and 52 weeks per year for a full-time role.
                    Multiply it by 20 hours per week and 52 weeks per year for a part-time role.
                    If the salary is given as a monthly rate, multiply it by 12 months to convert it into an annual salary.
                    If the salary is already provided on an annual basis, no further calculations are needed.
                    Consider any additional details from the job description (e.g., internship or contract duration) to ensure the calculated salary is reflective of the role.
                    Finally, provide the calculated salary in per annum and include the city, state, and country as mentioned in the job description. Ensure all calculations are accurate and based on the details provided in the job description."""
                    + job_responce.text,
                }
            ],
            format={
                "type": "object",
                "properties": {
                    "company_name": {"type": "string"},
                    "salary_min": {"type": "number"},
                    "salary_max": {"type": "number"},
                    "currency": {"type": "string"},
                    "city": {"type": "string"},
                    "state": {"type": "string"},
                    "country": {"type": "string"},
                },
                "required": [
                    "company_name",
                    "salary_min",
                    "salary_max",
                    "currency",
                    "city",
                    "state",
                    "country",
                ],
            },
        )

        # end timer here
        end_time = time.time()
        time_taken = end_time - start_time
        time_taken_in_seconds = round(time_taken, 2)
        print(f"Time taken: {time_taken_in_seconds}, model used: {model}")
        response_content2 = json.loads(response["message"]["content"])
        print(
            "From job:",
            response_content2.get("company_name"),
            response_content2.get("salary_min"),
            response_content2.get("salary_max"),
            response_content2.get("currency"),
            response_content2.get("city"),
            response_content2.get("state"),
            response_content2.get("country"),
        )

        # save all the details in a csv
        with open("company-jobs-models.csv", "a") as file:
            file.write(
                f"{model},"
                f"{company_url},"
                f"{internal_url + job_link},"
                f"{time_taken_in_seconds},"
                f"{response_content2.get('company_name')},"
                f"{response_content2.get('salary_min')},"
                f"{response_content2.get('salary_max')},"
                f"{response_content2.get('currency')},"
                f"{response_content2.get('city')},"
                f"{response_content2.get('state')},"
                f"{response_content2.get('country')}\n"
            )
