from site_helper.base import AbstractSiteHelper as _AbstractSiteHelper, ParserHelper as _ParserHelper
from requests import post as _requestPost, Response as _Response
from urllib.parse import urlencode as _urlEncode

from job_info import JobInfo
from site_types import SiteType
from status_types import StatusType


class CakeresumeHelper(_AbstractSiteHelper):
    def __init__(self) -> None:
        super().__init__()
        self._total_pages: int = 999
        self._current_page: int = 0

    def reset(self):
        self._total_pages = 999
        self._current_page = 0

    def _doRequestJobs(self, *args) -> _Response:
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

        SEARCH_JSON["requests"][0]["params"] += f"&page={self._current_page}"
        url = URL + _urlEncode(PARAMS)
        return _requestPost(url, json=SEARCH_JSON)

    def _doParseJobsResponse(self, resp: _Response) -> list[JobInfo]:
        content = _ParserHelper.convertContentToObject(
            resp.content.decode('utf-8'))

        if content == None:
            self._current_page = self._total_pages
            return []

        self._total_pages = content["results"][0]["nbPages"]
        self._current_page += 1

        hits_list = _ParserHelper.getValue(content, "results")
        if hits_list == None or not isinstance(hits_list, list):
            print("ERROR: CakeresumeHelper::_doParseJobsResponse got invalid results.")
            return result

        hits = _ParserHelper.getValue(hits_list[0], "hits")
        result: list[JobInfo] = []
        if hits == None or not isinstance(hits, list):
            print("ERROR: CakeresumeHelper::_doParseJobsResponse got invalid hits.")
            return result

        for info in hits:
            detail = JobInfo()
            detail.title = _ParserHelper.getValue(info, 'title')
            detail.company = _ParserHelper.getValue(info, 'page', 'name')
            detail.location = _ParserHelper.getValue(info, 'flat_location_list', 0) or ""
            detail.updated_time = int(_ParserHelper.getValue(info, 'content_updated_at'))
            detail.url = "https://www.cakeresume.com/companies/{}/jobs/{}".format(
                _ParserHelper.getValue(info, 'page', 'path'),
                _ParserHelper.getValue(info, 'path'))

            # we clip updated_time since it is in milliseconds.
            detail.updated_time = int(detail.updated_time/1000)

            detail.platform = SiteType.CAKERESUME.name
            detail.status = StatusType.UNREAD.value

            if not detail:
                print("ERROR: CakeresumeHelper::_doParseJobsResponse got invalid job info.")
                continue
            result.append(detail)
        return result

    def _hasRemainingJobs(self) -> bool:
        return self._current_page < self._total_pages
