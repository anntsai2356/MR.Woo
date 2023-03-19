import requests
import json
import math
from urllib.parse import urlencode
from jobs_parser import OZFJobsParser, JobInfo

root_url = "https://www.104.com.tw/jobs/search/list?"
params = {
    "ro": 0,
    "kwop": 7,
    "keyword": "後端工程師",
    "expansionType": "area,spec,com,job,wf,wktm",
    "order": 14,
    "asc": 0,
    # "page": 6,
    "mode": "s",
    "jobsource": "2018indexpoc",
    "langFlag": 0,
    "langStatus": 0,
    "recommendJob": 1,
    "hotJob": 1,
}
headers ={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
        'Referer': 'https://www.104.com.tw/jobs/search/',
}

def getPageCount():
    url = root_url + urlencode(params)
    response = requests.get(url, headers=headers)

    response.encoding = "utf-8"
    decoded_content = response.content.decode(response.encoding)

    data = json.loads(decoded_content)
    page_count = data["data"]['totalPage']

    return page_count

def getJobsFromPages(page_count):
    total_jobs: list[JobInfo] = []
    i = 1
    while i <= page_count:
        params["page"] = i
        url = root_url + urlencode(params)
        response = requests.get(url, headers=headers)
        response.encoding = "utf-8"
        decoded_content = response.content.decode(response.encoding)

        parser = OZFJobsParser()
        page_jobs = parser.parse(decoded_content)

        total_jobs += page_jobs
        i += 1

    return total_jobs

def export(total_jobs):
    import csv

    with open("../temp/ozf.csv", "w", encoding="utf-8", newline="") as f:
        csvfile = csv.DictWriter(f, fieldnames=JobInfo.fieldnames())
        csvfile.writeheader()
        for job in total_jobs:
            csvfile.writerow(job.toBuiltinDict())

# collect all raw data from api
page_count = getPageCount()
total_jobs = getJobsFromPages(page_count)

# write data to csv
export(total_jobs)