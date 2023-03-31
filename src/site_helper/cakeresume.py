from site_helper.base import AbstractSiteHelper as _AbstractSiteHelper, ParserHelper as _ParserHelper
from requests import post as _requestPost, Response as _Response
from urllib.parse import urlencode as _urlEncode
import requests
import json
import re

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
        search_page_url = "https://www.cakeresume.com/jobs"
        algolia = self.getCakeresumeToken(search_page_url)

        URL = "https://966rg9m3ek-dsn.algolia.net/1/indexes/*/queries?"
        # TODO: handle x-algolia-api-key
        PARAMS = {
            "x-algolia-agent": "Algolia for JavaScript (4.14.2); Browser (lite); instantsearch.js (4.49.1); react (18.2.0); react-instantsearch (6.38.1); react-instantsearch-hooks (6.38.1); JS Helper (3.11.1)",
            "x-algolia-api-key": algolia["api_key"],
            "x-algolia-application-id": algolia["app_id"],
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

            detail.site = SiteType.CAKERESUME.name
            detail.status = StatusType.UNREAD.value

            if not detail:
                print("ERROR: CakeresumeHelper::_doParseJobsResponse got invalid job info.")
                continue
            result.append(detail)
        return result

    def _hasRemainingJobs(self) -> bool:
        return self._current_page < self._total_pages

    def getCakeresumeToken(self, url: str) -> dict:
        """
        url : The url is page that use search box.

        There has many keys in cake resume.
        only key_jobs_and_pages is used to search Job index.

        Ex:
        {
            "algolia": {
                "id": "966RG9M3EK",
                "key": "NjNhZ...", (length = 620)
                "key_global_search": "MzA0M2...", (length = 284)
                "key_query_suggestions": "MDliO...", (length = 396)
                "key_users": "ZTZiM...", (length = 360)
                "key_jobs_and_pages": "NDM0O...", (length = 520)
                "key_featured_pages": "ZGUxY...", (length = 312)
                "key_featured_jobs": "NmU1M...", (length = 476)
                "key_published_posts": "ZThhN...", (length = 316)
                "key_organizations": "OTkwZ...", (length = 252)
                "key_activities": "MmYwN...", (length = 244)
                "key_articles": "OThkM...", (length = 292)
                "key_featured_items_tw_user": "MDgyY...", (length = 356)
                "key_featured_items_non_tw_user": "ZDM1Y..." (length = 423)
            }
        }
        """

        result = {"app_id": "", "api_key": ""}

        response = requests.get(url)
        response.encoding = "utf-8"
        decoded_content = response.content.decode(response.encoding)

        match = re.search('("algolia"?):{(.+?)}', decoded_content).group()
        match = "{" + match + "}"
        info = json.loads(match.replace("'", '"'))

        if not info["algolia"]["id"] and not info["algolia"]["key_jobs_and_pages"]:
            print(f"WARN: Could not find algolia keys in {url}.")
            return result

        result["app_id"] = info["algolia"]["id"]
        result["api_key"] = info["algolia"]["key_jobs_and_pages"]

        return result    
