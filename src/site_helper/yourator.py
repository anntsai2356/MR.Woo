from site_helper.base import AbstractSiteHelper as _AbstractSiteHelper, ParserHelper as _ParserHelper
from requests import get as _requestGet, Response as _Response
from urllib.parse import urlencode as _urlEncode
from math import ceil as _ceil
from time import mktime as _mktime
from datetime import datetime as _datetime

from job_info import JobInfo
from site_types import SiteType
from status_types import StatusType


class YouratorHelper(_AbstractSiteHelper):
    def __init__(self) -> None:
        super().__init__()
        self._total_pages: int = 999
        self._current_page: int = 1

    def reset(self):
        self._total_pages = 999
        self._current_page = 1

    def _doRequestJobs(self, *args):
        URL = "https://www.yourator.co/api/v2/jobs?"
        PARAMS = {
            "category[]": "後端工程",
            # "category[]": "全端工程", # 有多個分類的話，結果會混再一起再用更新日期排序
            "area[]": "TPE",
            "position[]": "full_time",
            "sort": "recent_updated",
            # "page": 1 # 20 per page
        }
        PARAMS["page"] = self._current_page
        url = URL + _urlEncode(PARAMS)
        return _requestGet(url)

    def _doParseJobsResponse(self, resp: _Response) -> list[JobInfo]:
        content = _ParserHelper.convertContentToObject(
            resp.content.decode('utf-8'))

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

            detail.platform = SiteType.YOURATOR.name
            detail.status = StatusType.UNREAD.value

            if not detail:
                print("ERROR: YouratorHelper::_doParseJobsResponse got invalid job info.")
                continue
            result.append(detail)
        return result

    def _hasRemainingJobs(self) -> bool:
        return self._current_page < self._total_pages
