import json
import re
import requests

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


        data = {
            "model": model,
            "prompt": """
            You are tasked to analyze a job description and extract specific information.
            Provide the main company name from the job description in the field `company_name`.
            Analyze the job description step-by-step to determine the minimum annual salary and maximum annual salary for the role. The calculation should be based on the following factors:  
            - Company information  
            - Location  
            - Job title  
            - Experience required  
            - Industry standards
            Follow these steps for accurate salary determination:  
            1. Analyze salary information provided in the job description:  
            - If the salary is specified directly in the description, extract and convert it into an annual format if necessary.  
            - If no salary is provided, use industry standards based on the other factors mentioned.  
            2. Account for the type of employment specified (e.g., full-time, part-time, contract, internship):  
            - For weekly rates:  
                - Multiply by 40 hours per week and 52 weeks per year for full-time roles.  
                - Multiply by 20 hours per week and 52 weeks per year for part-time roles.  
            - For monthly rates:  
                - Multiply by 12 months to convert into an annual salary.
            3. Provide the salary range:  
            - Ensure `minimum_annual_salary` and `maximum_annual_salary` are clearly stated.  
            - Use the international 3-letter currency code (e.g., USD, EUR, GBP, INR) for the salary values in the field `currency`.
            Additionally, provide the following information about the job location:  
            - City: Include the name of the city in the field `city`.  
            - State/Region: Specify the state or region in the field `state`.  
            - Country: Mention the country in the field `country`.
            
            Here is the job description:
            """
            + job_responce.text,
            "format": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string"},
                    "minimum_annual_salary": {"type": "number"},
                    "maximum_annual_salary": {"type": "number"},
                    "currency": {"type": "string"},
                    "city": {"type": "string"},
                    "state": {"type": "string"},
                    "country": {"type": "string"},
                },
                "required": [
                    "company_name",
                    "minimum_annual_salary",
                    "maximum_annual_salary",
                    "currency",
                    "city",
                    "state",
                    "country",
                ],
            },
            "options": {
                "num_ctx": 4096,
            },
            "stream": False,
            "keep_alive": "10m",
        }

        url = "http://localhost:11434/api/generate"
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_content = json.loads(response.text)
        time_taken = round(response_content.get("total_duration") / 1000000000, 2)
        print("Time taken:", time_taken)
        job_data = json.loads(response_content["response"])
        print(
            "From job:",
            job_data.get("company_name"),
            job_data.get("minimum_annual_salary"),
            job_data.get("maximum_annual_salary"),
            job_data.get("currency"),
            job_data.get("city"),
            job_data.get("state"),
            job_data.get("country"),
        )

        # save all the details in a csv
        with open("company-jobs-models.csv", "a") as file:
            file.write(
                f"{model},"
                f"{company_url},"
                f"{internal_url + job_link},"
                f"{time_taken},"
                f"{job_data.get('company_name')},"
                f"{job_data.get('minimum_annual_salary')},"
                f"{job_data.get('maximum_annual_salary')},"
                f"{job_data.get('currency')},"
                f"{job_data.get('city')},"
                f"{job_data.get('state')},"
                f"{job_data.get('country')},"
            )
