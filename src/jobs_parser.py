import json
from time import mktime
from datetime import datetime
from job_info import JobInfo
from typing import Any

class JobsParser:
    """
    JobParser is just an abstract class, do not use this directly.
    """
    def __init__(self) -> None:
        pass

    def _parseImpl(self, json_obj: object) -> list[JobInfo]:
        assert False, "JobParser::_parseImpl is not implemented yet."

    def parse(self, decoded_content: str) -> list[JobInfo]:
        try:
            obj = json.loads(decoded_content)
            return self._parseImpl(obj)

        except ValueError:
            print("ERROR: JobParser::parse failed to parse content: {}".format(content[:20] + "..."))
            return []

    @staticmethod
    def _getValueRecursively(obj: object, *keys) -> Any | None:
        for key in keys:
            assert isinstance(key, str), f"Only accept str typed key: {key}"
            if not isinstance(obj, object):
                print ("ERROR: JobParser::_getValueRecursively cannot parse non-object item.")
                return None
            if key not in obj:
                print(f"WARN: Value for key '{key}' not found.")
                return None
            obj = obj[key]
        return obj


class YouratorJobsParser(JobsParser):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def __reformURL(url):
        return f'https://www.yourator.co/{url}'

    def _parseImpl(self, json_obj: object) -> list[JobInfo]:
        result: list[JobInfo] = []
        for info in self._getValueRecursively(json_obj, "jobs"):
            detail = JobInfo()
            detail.title = self._getValueRecursively(info, 'name')
            detail.company = self._getValueRecursively(info, 'company', 'brand')
            detail.location = self._getValueRecursively(info, 'company', 'area')
            detail.updated_time = self._getValueRecursively(info, 'category', 'updated_at')
            detail.url = "https://www.yourator.co" + self._getValueRecursively(info, 'path')

            if not detail.updated_time:
                print("ERROR: YouratorJonsParser::_parseImpl got invalid time.")
                continue

            detail.updated_time = int(mktime(datetime.fromisoformat(detail.updated_time).timetuple()))

            if not detail:
                print("ERROR: YouratorJonsParser::_parseImpl got invalid job info.")
                continue
            result.append(detail)
        return result


class CakeresumeJobsParser(JobsParser):
    def __init__(self) -> None:
        super().__init__()

    def _parseImpl(self, json_obj: object) -> list[JobInfo]:
        hits_list = self._getValueRecursively(json_obj, "results")
        if not hits_list or not isinstance(hits_list, list):
            print("ERROR: CakeresumeJobsParser::_parseImpl got invalid results.")
            return result

        hits = self._getValueRecursively(hits_list[0], "hits")
        result: list[JobInfo] = []
        if not hits or not isinstance(hits, list):
            print("ERROR: CakeresumeJobsParser::_parseImpl got invalid hits.")
            return result

        for info in hits:
            detail = JobInfo()
            detail.title = self._getValueRecursively(info, 'title')
            detail.company = self._getValueRecursively(info, 'page', 'name')
            detail.location = self._getValueRecursively(info, 'flat_location_list')[0]
            detail.updated_time = int(self._getValueRecursively(info, 'content_updated_at'))
            detail.url = "https://www.cakeresume.com/companies/{}/jobs/{}".format(
                self._getValueRecursively(info, 'page', 'path'),
                self._getValueRecursively(info, 'path'))

            # we clip updated_time since it is in milliseconds.
            detail.updated_time = int(detail.updated_time/1000)
            if not detail:
                print("ERROR: CakeresumeJobsParser::_parseImpl got invalid job info.")
                continue
            result.append(detail)
        return result


class OZFJobsParser(JobsParser):
    def __init__(self) -> None:
        super().__init__()

    def _parseImpl(self, json_obj: object) -> list[JobInfo]:
        job_list = self._getValueRecursively(json_obj, "data", "list")
        result: list[JobInfo] = []
        if not job_list or not isinstance(job_list, list):
            print("ERROR: OZFJobsParser::_parseImpl got invalid hits.")
            return result

        for info in job_list:
            detail = JobInfo()
            detail.title = self._getValueRecursively(info, 'jobName')
            detail.company = self._getValueRecursively(info, 'custName')
            detail.location = self._getValueRecursively(info, 'jobAddrNoDesc') + self._getValueRecursively(info, 'jobAddress')
            updated_time = self._getValueRecursively(info, 'appearDate')
            detail.url = "https:" + self._getValueRecursively(info, 'link', 'job')

            if not updated_time:
                print("ERROR: OZFJobsParser::_parseImpl got invalid time.")
                continue

            create_datetime = datetime.strptime(updated_time, "%Y%m%d")
            detail.updated_time = int(mktime(create_datetime.timetuple()))

            if not detail:
                print("ERROR: OZFJobsParser::_parseImpl got invalid job info.")
                continue
            result.append(detail)
        return result


if __name__ == "__main__":
    import requests
    import json
    from urllib.parse import urlencode


    params = {
        "ro": 0,
        "kwop": 7,
        "keyword": "後端工程師",
        "expansionType": "area,spec,com,job,wf,wktm",
        "order": 14,
        "asc": 0,
        "page": 6,
        "mode": "s",
        "jobsource": "2018indexpoc",
        "langFlag": 0,
        "langStatus": 0,
        "recommendJob": 1,
        "hotJob": 1,
    }
    url = "https://www.104.com.tw/jobs/search/list?" + urlencode(params)

    headers ={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
            'Referer': 'https://www.104.com.tw/jobs/search/',
    }

    response = requests.get(url, headers=headers)

    response.encoding = 'utf-8'
    decoded_content = response.content.decode(response.encoding)
    # data = json.loads(decoded_content)
    # print(data)

    parser = OZFJobsParser()
    jobs = parser.parse(decoded_content)

    from pathlib import Path
    import csv
    with Path("tmp.csv").open("w", newline="\n") as f:
        csvfile = csv.DictWriter(f, fieldnames=JobInfo.fieldnames())
        csvfile.writeheader()
        for job in jobs:
            csvfile.writerow(job.toObject())

    with Path("tmp.csv").open("r") as f:
        for row in csv.DictReader(f):
            j = JobInfo(row)
            print(j)