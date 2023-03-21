import csv
import json
import math
import pathlib
import requests
from job_info import JobInfo
from jobs_parser import YouratorJobsParser
from urllib.parse import urlencode

base_directory = pathlib.Path(__file__).parents[1]

class YouratorHelper:
    root_url = "https://www.yourator.co/api/v2/jobs?"
    params = {
        "category[]": "後端工程",
        # "category[]": "全端工程", # 有多個分類的話，結果會混再一起再用更新日期排序
        "area[]": "TPE",
        "position[]": "full_time",
        "sort": "recent_updated",
        # "page": 1 # 20 per page
    }

    def __init__(self) -> None:
        pass

    def _getPageCount(self) -> int:
        url = self.root_url + urlencode(self.params)
        response = requests.get(url)

        response.encoding = "utf-8"
        decoded_content = response.content.decode(response.encoding)

        data = json.loads(decoded_content)
        total_jobs = data["total"]
        per_page = 20
        page_count = math.ceil(total_jobs / per_page)

        return page_count

    def _getJobsFromPages(self, page_count) -> list:
        total_jobs: list[JobInfo] = []
        i = 1
        while i <= page_count:
            self.params["page"] = i
            url = self.root_url + urlencode(self.params)
            response = requests.get(url)
            response.encoding = "utf-8"
            decoded_content = response.content.decode(response.encoding)

            parser = YouratorJobsParser()
            page_jobs = parser.parse(decoded_content)

            total_jobs += page_jobs
            i += 1

        return total_jobs

    def export(self):
        # collect all raw data from api
        page_count = self._getPageCount()
        total_jobs = self._getJobsFromPages(page_count)

        # write data to csv
        with pathlib.Path(base_directory).joinpath("temp", "yourator.csv").open(
            "w", encoding="utf-8", newline=""
        ) as f:
            csvfile = csv.DictWriter(f, fieldnames=JobInfo.fieldnames())
            csvfile.writeheader()
            for job in total_jobs:
                csvfile.writerow(job.toBuiltinDict())

if __name__ == "__main__":
    helper = YouratorHelper()
    helper.export()