from site_helper.base import AbstractSiteHelper as _AbstractSiteHelper, ParserHelper as _ParserHelper
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

    def reset(self):
        self._total_pages = 999
        self._current_page = 1

    def _doRequestJobs(self, *args) -> _Response:
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
        PARAMS["page"] = self._current_page

        url = URL + _urlEncode(PARAMS)
        return _requestGet(url, headers=HEADERS)

    def _doParseJobsResponse(self, resp: _Response) -> list[JobInfo]:
        content = _ParserHelper.convertContentToObject(
            resp.content.decode('utf-8'))

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

            detail.platform = SiteType.OZF.name
            detail.status = StatusType.UNREAD.value

            if not detail:
                print("ERROR: OZFHelper::_doParseJobsResponse got invalid job info.")
                continue
            result.append(detail)
        return result

    def _hasRemainingJobs(self) -> bool:
        return self._current_page <= self._total_pages
