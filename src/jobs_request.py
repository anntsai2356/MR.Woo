from jobs_parser import OZFJobsParser, CakeresumeJobsParser, YouratorJobsParser
from job_info import JobInfo
from urllib.parse import urlencode
from site_types import SiteType
import json
import math
import requests


class RequestHelper:
    """
    Class RequestHelper requests the job information from RequestHelper::SiteType.

    Using RequestHelperHandle.get() to construct a concrete RequestHelper instead of
    calling RequestHelper() directly.
    """

    def __init__(self, site_type: SiteType = SiteType.UNSUPPORTED) -> None:
        assert type(
            self) != RequestHelper, "ERROR: use RequestHelperHandle.get() instead."
        self._type: SiteType = site_type

    def __getJobs(self, out_jobs_list: list[JobInfo]) -> bool:
        """
        Request the jobs' information.

        The jobs should be appended in-place in the list |out_jobs_list|,
        and the return value means whether there still have the remaining jobs
        information.
        """
        response = self._getResponse()
        if response.status_code != 200:
            print(
                f"WARN: get HTTP status code {response.status_code} from URL {response.url}")
            return False
        return self._paserResponse(response.content.decode("utf-8"), out_jobs_list)

    @staticmethod
    def __checkIfListIsValid(target: list[JobInfo]):
        """
        Check whether all job information in |target| is valid.
        """
        for info in target:
            if not isinstance(info, JobInfo) or not info:
                return False
        return True

    def _paserResponse(self, decoded_content: str, out_jobs_list: list[JobInfo]) -> bool:
        """
        Parse the response from certain sites.

        The jobs should be appended in-place in the list |out_jobs_list|,
        and the return value means whether there still have the remaining jobs
        information.

        Returns the identifier of whether job information is left.
        """
        assert False, "RequestHelper::_paserResponse is not implemented yet."

    def _getResponse(self) -> requests.Response:
        """
        Request to certain sites and obtain response from them.
        """
        assert False, "RequestHelper::_getResponse is not implemented yet."

    def siteType(self) -> SiteType:
        return self._type

    def getJobsList(self) -> list[JobInfo]:
        """
        Request the jobs informations.
        """
        # TODO: dynamic query keyword
        result: list[JobInfo] = []

        while self.__getJobs(result):
            if not self.__checkIfListIsValid(result):
                print("ERROR: RequestHelper::getJobsList got invalid job information.")
                return []

        return result


class _OZFRequestHelperImpl(RequestHelper):
    def __init__(self) -> None:
        super().__init__(SiteType.OZF)
        self._total_pages: int = 999
        self._queried_pages: int = 1

    def _getResponse(self) -> requests.Response:
        URL = "https://www.104.com.tw/jobs/search/list?"
        PARAMS = {
            "ro": 0,
            "kwop": 7,
            "keyword": "後端工程師",
            "expansionType": "area,spec,com,job,wf,wktm",
            "order": 14,
            "asc": 0,
            "mode": "s",
            "jobsource": "2018indexpoc",
            "langFlag": 0,
            "langStatus": 0,
            "recommendJob": 1,
            "hotJob": 1,
            "area": "6001001000,6001002000",  # 6001001000: 台北市; 6001002000: 新北市
        }
        HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36",
            "Referer": "https://www.104.com.tw/jobs/search/",
        }
        PARAMS["page"] = self._queried_pages

        url = URL + urlencode(PARAMS)
        return requests.get(url, headers=HEADERS)

    def _paserResponse(self, decoded_content: str, out_jobs_list: list[JobInfo]) -> bool:
        data = json.loads(decoded_content)
        self._total_pages = data["data"]["totalPage"]
        self._queried_pages += 1

        out_jobs_list += OZFJobsParser().parse(decoded_content)

        return self._queried_pages <= self._total_pages


class _CakeresumeRequestHelperImpl(RequestHelper):
    def __init__(self) -> None:
        super().__init__(SiteType.CAKERESUME)
        self._total_pages: int = 999
        self._queried_pages: int = 0

    def _getResponse(self) -> requests.Response:
        URL = "https://966rg9m3ek-dsn.algolia.net/1/indexes/*/queries?"
        # TODO: handle x-algolia-api-key
        PARAMS = {
            "x-algolia-agent": "Algolia for JavaScript (4.14.2); Browser (lite); instantsearch.js (4.49.1); react (18.2.0); react-instantsearch (6.38.1); react-instantsearch-hooks (6.38.1); JS Helper (3.11.1)",
            "x-algolia-api-key": "ZThkNmExMWRiZjQ4ZGJlZWU4YTc1MTEyN2U2Y2ViZTUxMWM1MTdlODM4YWE2MWYzYThhZWI1NzZiM2Y5ZTI5N3ZhbGlkVW50aWw9MTY4MDYyMjk1MSZyZXN0cmljdEluZGljZXM9Sm9iJTJDSm9iX29yZGVyX2J5X2NvbnRlbnRfdXBkYXRlZF9hdCUyQ0pvYl9wbGF5Z3JvdW5kJTJDUGFnZSUyQ1BhZ2Vfb3JkZXJfYnlfY29udGVudF91cGRhdGVkX2F0JmZpbHRlcnM9YWFzbV9zdGF0ZSUzQSslMjJjcmVhdGVkJTIyK0FORCtub2luZGV4JTNBK2ZhbHNlJmhpdHNQZXJQYWdlPTEwJmF0dHJpYnV0ZXNUb1NuaXBwZXQ9JTVCJTIyZGVzY3JpcHRpb25fcGxhaW5fdGV4dCUzQTgwJTIyJTVEJmhpZ2hsaWdodFByZVRhZz0lM0NtYXJrJTNFJmhpZ2hsaWdodFBvc3RUYWc9JTNDJTJGbWFyayUzRQ==",
            "x-algolia-application-id": "966RG9M3EK",
        }
        SEARCH_JSON = {
            "requests": [
                {
                    "indexName": "Job",
                    # "params": "clickAnalytics=true&distinct=false&enablePersonalization=true&facets=%5B%22location_list%22%2C%22profession%22%2C%22job_type%22%2C%22seniority_level%22%2C%22salary_range%22%2C%22remote%22%2C%22year_of_seniority%22%2C%22number_of_management%22%2C%22page.number_of_employees%22%2C%22page.sector%22%2C%22page.tech_labels%22%2C%22lang_name%22%2C%22salary_type%22%2C%22salary_currency%22%5D&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&maxValuesPerFacet=500&page=0&query=php&tagFilters=&userToken=39196",
                    # "params": "page=0&query=php&userToken=39196",
                    "params": "query=php&userToken=39196",
                }
            ]
        }

        SEARCH_JSON["requests"][0]["params"] += f"&page={self._queried_pages}"
        url = URL + urlencode(PARAMS)
        return requests.post(url, json=SEARCH_JSON)

    def _paserResponse(self, decoded_content: str, out_jobs_list: list[JobInfo]) -> bool:
        data = json.loads(decoded_content)
        self._total_pages = data["results"][0]["nbPages"]
        self._queried_pages += 1

        out_jobs_list += CakeresumeJobsParser().parse(decoded_content)

        return self._queried_pages < self._total_pages


class _YouratorRequestHelperImpl(RequestHelper):
    def __init__(self) -> None:
        super().__init__(SiteType.CAKERESUME)
        self._total_pages: int = 999
        self._queried_pages: int = 1

    def _getResponse(self) -> requests.Response:
        URL = "https://www.yourator.co/api/v2/jobs?"
        PARAMS = {
            "category[]": "後端工程",
            # "category[]": "全端工程", # 有多個分類的話，結果會混再一起再用更新日期排序
            "area[]": "TPE",
            "position[]": "full_time",
            "sort": "recent_updated",
            # "page": 1 # 20 per page
        }
        PARAMS["page"] = self._queried_pages
        url = URL + urlencode(PARAMS)
        return requests.get(url)

    def _paserResponse(self, decoded_content: str, out_jobs_list: list[JobInfo]) -> bool:
        data = json.loads(decoded_content)
        self._total_pages = math.ceil(data["total"] / 20)
        self._queried_pages += 1

        out_jobs_list += YouratorJobsParser().parse(decoded_content)

        return self._queried_pages <= self._total_pages


class RequestHelperHandle:
    """
    Class RequestHelperHandle constructs a concrete RequestHelper object.
    """

    def __init__(self) -> None:
        assert False, "RequestHelperHandle should not construct."

    @staticmethod
    def get(type: SiteType = SiteType.UNSUPPORTED) -> RequestHelper:
        """
        Get the specific RequestHelper by the given SiteType |type|.
        """
        if type == SiteType.OZF:
            return _OZFRequestHelperImpl()
        elif type == SiteType.YOURATOR:
            return _YouratorRequestHelperImpl()
        elif type == SiteType.CAKERESUME:
            return _CakeresumeRequestHelperImpl()
        assert False, "ERROR: Unsupport request type"


if __name__ == "__main__":
    helper = RequestHelperHandle.get(SiteType.CAKERESUME)
    jobs = helper.getJobsList()
    for j in jobs:
        print(j)
        print()
