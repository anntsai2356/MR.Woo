import re as _re
from site_helper.base import AbstractSiteHelper as _AbstractSiteHelper, ParserHelper as _ParserHelper, JobDetails as _JobDetails
from site_param_helper import SiteParamHelperHandle
from requests import get as _requestGet, Response as _Response
from urllib.parse import urlencode as _urlEncode
from time import mktime as _mktime
from datetime import datetime as _datetime

from job_info import JobInfo
from site_types import SiteType
from status_types import StatusType


class OZFHelper(_AbstractSiteHelper):
    def __init__(self) -> None:
        super().__init__()
        self._total_pages: int = 999
        self._current_page: int = 1
        self._cached_details: _JobDetails = None

    def reset(self):
        self._total_pages = 999
        self._current_page = 1
        self._cached_details = None

    def _doRequestJobs(self, *args, **kwargs) -> _Response:
        """
        kwargs: give query parameters and values

        ex. keyword = 'php'

        The valid parameter list is set in {Site}ParamHelper.
        """
        
        URL = "https://www.104.com.tw/jobs/search/list?"

        param_helper = SiteParamHelperHandle.get(SiteType.OZF)
        query = param_helper.getQuery(**kwargs)
        PARAMS = query

        HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36",
            "Referer": "https://www.104.com.tw/jobs/search/",
        }
        PARAMS["page"] = self._current_page

        url = URL + _urlEncode(PARAMS)
        return _requestGet(url, headers=HEADERS)

    def _doParseJobsResponse(self, resp: _Response) -> list[JobInfo]:
        content = _ParserHelper.convertContentToObject(resp.content.decode('utf-8'))

        if content == None:
            self._current_page = self._total_pages
            return []

        self._total_pages = content["data"]["totalPage"]
        self._current_page += 1

        job_list = _ParserHelper.getValue(content, "data", "list")
        result: list[JobInfo] = []
        if job_list == None or not isinstance(job_list, list):
            print("ERROR: OZFHelper::_doParseJobsResponse got invalid hits.")
            return result

        for info in job_list:
            detail = JobInfo()
            detail.title = _ParserHelper.getValue(info, 'jobName')
            detail.company = _ParserHelper.getValue(info, 'custName')
            detail.location = _ParserHelper.getValue(info, 'jobAddrNoDesc') + _ParserHelper.getValue(info, 'jobAddress')
            updated_time = _ParserHelper.getValue(info, 'appearDate')
            detail.url = "https:" + _ParserHelper.getValue(info, 'link', 'job')

            if not updated_time:
                print("ERROR: OZFHelper::_doParseJobsResponse got invalid time.")
                continue

            create_datetime = _datetime.strptime(updated_time, "%Y%m%d")
            detail.updated_time = int(_mktime(create_datetime.timetuple()))

            detail.site = SiteType.OZF
            detail.status = StatusType.UNREAD

            if not detail:
                print("ERROR: OZFHelper::_doParseJobsResponse got invalid job info.")
                continue
            result.append(detail)
        return result

    def _hasRemainingJobs(self) -> bool:
        return self._current_page <= self._total_pages

    def _getCachedJobDetails(self, info: JobInfo) -> _JobDetails:
        return self._cached_details

    def _requestJobDetails(self, info: JobInfo) -> _Response:
        id_mat = _re.search("https:\/\/www\.104\.com\.tw\/job\/(\w+)(?:\?.*)?", info.url)
        if not id_mat:
            print(f"ERROR: failed to get id from {info.url}")
            resp = _Response()
            resp.status_code = 404
            resp.url = info.url
            return resp

        HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36",
            "Referer": "https://www.104.com.tw/jobs/search/",
        }
        return _requestGet(f"https://www.104.com.tw/job/ajax/content/{id_mat.group(1)}", headers=HEADERS)

    def _doParseJobDetails(self, resp: _Response) -> _JobDetails:
        content = _ParserHelper.convertContentToObject(resp.content.decode('utf-8'))

        self._cached_details = _JobDetails()
        self._cached_details.overview = _ParserHelper.getValue(content, "data", "jobDetail", "jobDescription")
        self._cached_details.responsibilities = ""
        if exp_req := _ParserHelper.getValue(content, "data", "condition", "workExp"):
            self._cached_details.requirements = f"工作經歷 {exp_req}\n\n"
        self._cached_details.requirements += _ParserHelper.getValue(content, "data", "condition", "other")

        return self._cached_details
