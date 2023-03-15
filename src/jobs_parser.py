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

    def parse(self, content: str) -> list[JobInfo]:
        try:
            obj = json.loads(content)
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
            detail.created_time = self._getValueRecursively(info, 'category', 'created_at')
            detail.updated_time = self._getValueRecursively(info, 'category', 'updated_at')
            detail.url = self._getValueRecursively(info, 'path')

            if not detail.created_time or not detail.updated_time:
                print("ERROR: YouratorJonsParser::_parseImpl got invalid time.")
                continue

            detail.created_time = int(mktime(datetime.fromisoformat(detail.created_time).timetuple()))
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
            create_time = self._getValueRecursively(info, 'created_at')
            detail.updated_time = int(self._getValueRecursively(info, 'content_updated_at'))
            detail.url = "{}/jobs/{}".format(self._getValueRecursively(info, 'page', 'path'),
                                        self._getValueRecursively(info, 'path'))

            if not create_time:
                print("ERROR: CakeresumeJobsParser::_parseImpl got invalid time.")
                continue

            create_time = create_time[:-5]
            create_datetime = datetime.fromisoformat(create_time)
            detail.created_time = int(mktime(create_datetime.timetuple()))

            # we clip updated_time since it is in milliseconds.
            detail.updated_time = int(detail.updated_time/1000)
            if not detail:
                print("ERROR: CakeresumeJobsParser::_parseImpl got invalid job info.")
                continue
            result.append(detail)
        return result


if __name__ == "__main__":
    import requests
    import json
    from urllib.parse import urlencode

    params = {
        "x-algolia-agent": "Algolia for JavaScript (4.14.2); Browser (lite); instantsearch.js (4.49.1); react (18.2.0); react-instantsearch (6.38.1); react-instantsearch-hooks (6.38.1); JS Helper (3.11.1)",
        "x-algolia-api-key": "OTQ1MjI1MmYwNmM0YmQ0MjIxMTZhNzM1NWNhZGQ0YzQ5OGM2Y2I5NzQ1ZTM1MjViMTMyMTE0NTk3MTZkODI2NHZhbGlkVW50aWw9MTY3OTMwODQ5NSZyZXN0cmljdEluZGljZXM9Sm9iJTJDSm9iX29yZGVyX2J5X2NvbnRlbnRfdXBkYXRlZF9hdCUyQ0pvYl9wbGF5Z3JvdW5kJTJDUGFnZSUyQ1BhZ2Vfb3JkZXJfYnlfY29udGVudF91cGRhdGVkX2F0JmZpbHRlcnM9YWFzbV9zdGF0ZSUzQSslMjJjcmVhdGVkJTIyK0FORCtub2luZGV4JTNBK2ZhbHNlJmhpdHNQZXJQYWdlPTEwJmF0dHJpYnV0ZXNUb1NuaXBwZXQ9JTVCJTIyZGVzY3JpcHRpb25fcGxhaW5fdGV4dCUzQTgwJTIyJTVEJmhpZ2hsaWdodFByZVRhZz0lM0NtYXJrJTNFJmhpZ2hsaWdodFBvc3RUYWc9JTNDJTJGbWFyayUzRQ==",
        "x-algolia-application-id": "966RG9M3EK",
    }
    url = "https://966rg9m3ek-dsn.algolia.net/1/indexes/*/queries?" + urlencode(params)

    search_json = {
        "requests": [
            {
                "indexName": "Job",
                "params": "clickAnalytics=true&distinct=false&enablePersonalization=true&facets=%5B%22location_list%22%2C%22profession%22%2C%22job_type%22%2C%22seniority_level%22%2C%22salary_range%22%2C%22remote%22%2C%22year_of_seniority%22%2C%22number_of_management%22%2C%22page.number_of_employees%22%2C%22page.sector%22%2C%22page.tech_labels%22%2C%22lang_name%22%2C%22salary_type%22%2C%22salary_currency%22%5D&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&maxValuesPerFacet=500&page=0&query=php&tagFilters=&userToken=39196",
            }
        ]
    }
    response = requests.post(url, json=search_json)

    decoded_content = response.content.decode('utf-8')

    from pathlib import Path
    Path("tmp.json").write_text(decoded_content)

    parser = CakeresumeJobsParser()
    jobs = parser.parse(decoded_content)

    for j in jobs:
        print()
        print(j)
        print()