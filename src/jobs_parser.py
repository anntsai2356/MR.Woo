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

            print(detail.created_time)
            print(detail.updated_time)
            detail.created_time = int(mktime(datetime.fromisoformat(detail.created_time).timetuple()))
            detail.updated_time = int(mktime(datetime.fromisoformat(detail.updated_time).timetuple()))

            if not detail:
                print("ERROR: YouratorJonsParser::_parseImpl got invalid job info.")
                continue
            result.append(detail)
        return result


if __name__ == "__main__":
    import requests
    import json
    from urllib.parse import urlencode

    params = {
        "category[]": "後端工程",
        "area[]": "TPE",
        "position[]": "full_time",
        "sort": "recent_updated",
        "page": 1
    }
    url = "https://www.yourator.co/api/v2/jobs?" + urlencode(params)

    response = requests.get(url)

    response.encoding = 'utf-8'
    decoded_content = response.content.decode(response.encoding)

    from pathlib import Path
    Path("tmp.json").write_text(decoded_content)

    parser = YouratorJobsParser()
    jobs = parser.parse(decoded_content)

    for j in jobs:
        print()
        print(j)
        print()