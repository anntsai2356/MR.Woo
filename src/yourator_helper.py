import requests
import json
import math
from urllib.parse import urlencode
from jobs_parser import YouratorJobsParser, JobInfo

root_url = "https://www.yourator.co/api/v2/jobs?"
params = {
    "category[]": "後端工程",
    # "category[]": "全端工程", # 有多個分類的話，結果會混再一起再用更新日期排序
    "area[]": "TPE",
    "position[]": "full_time",
    "sort": "recent_updated",
    # "page": 1 # 20 per page
}

def getPageCount():
    url = root_url + urlencode(params)
    response = requests.get(url)

    response.encoding = "utf-8"
    decoded_content = response.content.decode(response.encoding)

    data = json.loads(decoded_content)
    total_jobs = data["total"]
    per_page = 20
    page_count = math.ceil(total_jobs / per_page)

    return page_count

def getJobsFromPages(page_count):
    total_jobs: list[JobInfo] = []
    i = 1
    while i <= page_count:
        params["page"] = i
        url = root_url + urlencode(params)
        response = requests.get(url)
        response.encoding = "utf-8"
        decoded_content = response.content.decode(response.encoding)

        parser = YouratorJobsParser()
        page_jobs = parser.parse(decoded_content)

        total_jobs += page_jobs
        i += 1

    return total_jobs

def export(total_jobs):
    import csv

    with open('../temp/yourator.csv', "w", encoding="utf-8", newline="") as f:
        csvfile = csv.DictWriter(f, fieldnames=JobInfo.fieldnames())
        csvfile.writeheader()
        for job in total_jobs:
            csvfile.writerow(job.toBuiltinDict())

# collect all raw data from api
page_count = getPageCount()
total_jobs = getJobsFromPages(page_count)

# write data to csv
export(total_jobs)