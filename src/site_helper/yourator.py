from site_helper.base import AbstractSiteHelper as _AbstractSiteHelper, ParserHelper as _ParserHelper, JobDetails as _JobDetails
from site_param_helper import SiteParamHelperHandle
from requests import get as _requestGet, Response as _Response
from urllib.parse import urlencode as _urlEncode
from math import ceil as _ceil
from time import mktime as _mktime
from datetime import datetime as _datetime
from bs4 import BeautifulSoup as _bs

from job_info import JobInfo
from site_types import SiteType
from status_types import StatusType


class YouratorHelper(_AbstractSiteHelper):
    def __init__(self) -> None:
        super().__init__()
        self._total_pages: int = 999
        self._current_page: int = 1
        self._cached_details: _JobDetails = None

    def reset(self):
        self._total_pages = 999
        self._current_page = 1
        self._cached_details = None

    def _doRequestJobs(self, *args, **kwargs):
        """
        kwargs: give query parameters and values

        ex. keyword = 'php'

        The valid parameter list is set in {Site}ParamHelper.
        """

        URL = "https://www.yourator.co/api/v2/jobs?"

        param_helper = SiteParamHelperHandle.get(SiteType.OZF)
        query = param_helper.getQuery(**kwargs)        
        PARAMS = query
        PARAMS = {
            "term[]": "backend",
            # # "category[]": "全端工程", # 有多個分類的話，結果會混再一起再用更新日期排序
            # "area[]": "TPE",
            # "position[]": "full_time",
            # "sort": "recent_updated",
            # # "page": 1 # 20 per page
        }        

        PARAMS["page"] = self._current_page
        url = URL + _urlEncode(PARAMS)
        return _requestGet(url)

    def _doParseJobsResponse(self, resp: _Response) -> list[JobInfo]:
        content = _ParserHelper.convertContentToObject(resp.content.decode('utf-8'))

        if content == None:
            self._current_page = self._total_pages
            return []

        self._total_pages = _ceil(content["total"] / 20)
        self._current_page += 1

        result: list[JobInfo] = []
        for info in _ParserHelper.getValue(content, "jobs"):
            detail = JobInfo()
            detail.title = _ParserHelper.getValue(info, 'name')
            detail.company = _ParserHelper.getValue(info, 'company', 'brand')
            detail.location = _ParserHelper.getValue(info, 'company', 'area')
            detail.updated_time = _ParserHelper.getValue(info, 'category', 'updated_at')
            detail.url = "https://www.yourator.co" + _ParserHelper.getValue(info, 'path')

            if not detail.updated_time:
                print("ERROR: YouratorHelper::_doParseJobsResponse got invalid time.")
                continue

            detail.updated_time = int(_mktime(_datetime.fromisoformat(detail.updated_time).timetuple()))

            detail.site = SiteType.YOURATOR
            detail.status = StatusType.UNREAD

            if not detail:
                print("ERROR: YouratorHelper::_doParseJobsResponse got invalid job info.")
                continue
            result.append(detail)
        return result

    def _hasRemainingJobs(self) -> bool:
        return self._current_page <= self._total_pages

    def _getCachedJobDetails(self, info: JobInfo) -> _JobDetails:
        return self._cached_details

    def _requestJobDetails(self, info: JobInfo) -> _Response:
        HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36",
            "Referer": "https://www.104.com.tw/jobs/search/",
        }
        return _requestGet(info.url, headers=HEADERS)

    def _doParseJobDetails(self, resp: _Response) -> _JobDetails:
        sp = _bs(resp.content, "html.parser")

        self._cached_details = _JobDetails()
        job_content = sp.find("div", class_="job__content")
        details = job_content.find("section", class_="content__area unreset")
        self._cached_details.overview = details.text
        details = details.next
        self._cached_details.requirements = details.text

        return self._cached_details