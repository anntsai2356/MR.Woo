import requests
import json
import math
from urllib.parse import urlencode
from jobs_parser import CakeresumeJobsParser, JobInfo

params = {
    "x-algolia-agent": "Algolia for JavaScript (4.14.2); Browser (lite); instantsearch.js (4.49.1); react (18.2.0); react-instantsearch (6.38.1); react-instantsearch-hooks (6.38.1); JS Helper (3.11.1)",
    "x-algolia-api-key": "OTQ1MjI1MmYwNmM0YmQ0MjIxMTZhNzM1NWNhZGQ0YzQ5OGM2Y2I5NzQ1ZTM1MjViMTMyMTE0NTk3MTZkODI2NHZhbGlkVW50aWw9MTY3OTMwODQ5NSZyZXN0cmljdEluZGljZXM9Sm9iJTJDSm9iX29yZGVyX2J5X2NvbnRlbnRfdXBkYXRlZF9hdCUyQ0pvYl9wbGF5Z3JvdW5kJTJDUGFnZSUyQ1BhZ2Vfb3JkZXJfYnlfY29udGVudF91cGRhdGVkX2F0JmZpbHRlcnM9YWFzbV9zdGF0ZSUzQSslMjJjcmVhdGVkJTIyK0FORCtub2luZGV4JTNBK2ZhbHNlJmhpdHNQZXJQYWdlPTEwJmF0dHJpYnV0ZXNUb1NuaXBwZXQ9JTVCJTIyZGVzY3JpcHRpb25fcGxhaW5fdGV4dCUzQTgwJTIyJTVEJmhpZ2hsaWdodFByZVRhZz0lM0NtYXJrJTNFJmhpZ2hsaWdodFBvc3RUYWc9JTNDJTJGbWFyayUzRQ==",
    "x-algolia-application-id": "966RG9M3EK",
}
root_url = "https://966rg9m3ek-dsn.algolia.net/1/indexes/*/queries?"

search_json = {
    "requests": [
        {
            "indexName": "Job",
            # "params": "clickAnalytics=true&distinct=false&enablePersonalization=true&facets=%5B%22location_list%22%2C%22profession%22%2C%22job_type%22%2C%22seniority_level%22%2C%22salary_range%22%2C%22remote%22%2C%22year_of_seniority%22%2C%22number_of_management%22%2C%22page.number_of_employees%22%2C%22page.sector%22%2C%22page.tech_labels%22%2C%22lang_name%22%2C%22salary_type%22%2C%22salary_currency%22%5D&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&maxValuesPerFacet=500&page=0&query=php&tagFilters=&userToken=39196",
            # "params": "page=0&query=php&userToken=39196",
            "params": "query=php&userToken=39196",
        }
    ]
}

def getPageCount():
    url = root_url + urlencode(params)
    response = requests.post(url, json=search_json)

    response.encoding = "utf-8"
    decoded_content = response.content.decode(response.encoding)

    data = json.loads(decoded_content)
    page_count = data["results"][0]["nbPages"]

    return page_count

def getJobsFromPages(page_count):
    total_jobs: list[JobInfo] = []
    i = 0
    while i < page_count:
        search_json['requests'][0]['params'] += '&page=' + str(i)
        url = root_url + urlencode(params)
        response = requests.post(url, json=search_json)
        response.encoding = "utf-8"
        decoded_content = response.content.decode(response.encoding)

        parser = CakeresumeJobsParser()
        page_jobs = parser.parse(decoded_content)

        total_jobs += page_jobs
        i += 1

    return total_jobs

def export(total_jobs):
    import csv

    with open("../temp/cakeresume.csv", "w", encoding="utf-8", newline="") as f:
        csvfile = csv.DictWriter(f, fieldnames=JobInfo.fieldnames())
        csvfile.writeheader()
        for job in total_jobs:
            csvfile.writerow(job.toBuiltinDict())

# collect all raw data from api
page_count = getPageCount()
total_jobs = getJobsFromPages(page_count)

# write data to csv
export(total_jobs)