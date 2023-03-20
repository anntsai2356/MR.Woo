import csv
import json
import math
import pathlib
import requests
from jobs_parser import OZFJobsParser, JobInfo
from urllib.parse import urlencode

base_directory = pathlib.Path(__file__).parents[1]

class OzfHelper:
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36",
        "Referer": "https://www.104.com.tw/jobs/search/",
    }

    def __init__(self) -> None:
        pass

    def _getPageCount(self) -> int:
        url = self.root_url + urlencode(self.params)
        response = requests.get(url, headers=self.headers)

        response.encoding = "utf-8"
        decoded_content = response.content.decode(response.encoding)

        data = json.loads(decoded_content)
        page_count = data["data"]["totalPage"]

        return page_count

    def _getJobsFromPages(self, page_count) -> list:
        total_jobs: list[JobInfo] = []
        i = 1
        while i <= page_count:
            self.params["page"] = i
            url = self.root_url + urlencode(self.params)
            response = requests.get(url, headers=self.headers)
            response.encoding = "utf-8"
            decoded_content = response.content.decode(response.encoding)

            parser = OZFJobsParser()
            page_jobs = parser.parse(decoded_content)

            total_jobs += page_jobs
            i += 1

        return total_jobs

    def export(self):
        # collect all raw data from api
        page_count = self._getPageCount()
        total_jobs = self._getJobsFromPages(page_count)

        # write data to csv
        with pathlib.Path(base_directory).joinpath("temp", "ozf.csv").open(
            "w", encoding="utf-8", newline=""
        ) as f:
            csvfile = csv.DictWriter(f, fieldnames=JobInfo.fieldnames())
            csvfile.writeheader()
            for job in total_jobs:
                csvfile.writerow(job.toBuiltinDict())        

if __name__ == "__main__":
    helper = OzfHelper()
    helper.export()