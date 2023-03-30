from requests import Response as _Response
from abc import ABC, abstractmethod
from typing import TypeAlias
import json as _json

from job_info import JobInfo


class AbstractSiteHelper(ABC):
    """
    AbstractSiteHelper class is a virtual class that provides some implementations
    about Request and Response parsing.

    All functions in this class may have side-effect. e.g. |requestNext()| will cause
    the DerivedHelper to change their state to fetch different job information in the next time.
    """

    class _ContentParserHelper:
        @staticmethod
        def convertContentToObject(decoded_content: str) -> object | None:
            try:
                return _json.loads(decoded_content)
            except ValueError:
                print("ERROR: failed to parse content: {}".format(
                    decoded_content[:20] + "..."))
                return None

        @staticmethod
        def getValue(obj, *keys):
            for key in keys:
                if isinstance(obj, list):
                    if isinstance(key, int):
                        if key < len(obj):
                            obj = obj[key]
                        else:
                            # print(f"WARN: index '{key}' exceeds the object length {len(obj)}.")
                            return None
                    else:
                        # print(f"ERROR: attemp to access list with typed '{type(key).__name__}'.")
                        return None
                elif isinstance(obj, object):
                    if key in obj:
                        obj = obj[key]
                    else:
                        # print(f"WARN: the value for '{key}' not found.")
                        return None
            return obj

    def __init__(self) -> None:
        pass

    @abstractmethod
    def reset(self):
        """
        Reset the Helper state to make Helper re-usable.
        """
        return NotImplemented

    @abstractmethod
    def _doRequestJobs(self, *args) -> _Response:
        """
        Do fetch certain site with arguments |args| and return its response.
        """
        return NotImplemented

    @abstractmethod
    def _doParseJobsResponse(self, resp: _Response) -> list[JobInfo]:
        """
        Do parse the response from |_doRequestJobs()|.

        Only invoke this function when the HTTP response is 200.
        """
        return NotImplemented

    @abstractmethod
    def _hasRemainingJobs(self) -> bool:
        """
        Return whether there are remaining job information to be retrieved.
        """
        return NotImplemented

    def _onRequestJobsFailed(self, resp: _Response) -> bool:
        """
        The callback for Derived Helper deal with the response with non-200 status code.

        Return whether to re-request.
        """
        return False

    def __requestNextJobs(self, *args, out: list[JobInfo]) -> bool:
        """
        Request job's information of next page.

        The newer jobs should be appended in-place in the list |out|,
        and the return value means whether there still have the remaining jobs
        information.

        We will check http status code here.
        """
        resp = self._doRequestJobs(*args)

        if resp.status_code != 200:
            print(f"WARN: get HTTP status code {resp.status_code}")
            print(f"      from URL {resp.url}")
            return self._onRequestJobsFailed(resp)

        out += self._doParseJobsResponse(resp)
        return self._hasRemainingJobs()

    def requestJobs(self) -> list[JobInfo]:
        """
        Request for job information.
        """
        # TODO: dynamic query keyword
        result: list[JobInfo] = []

        while self.__requestNextJobs(out=result):
            pass

        return result



ParserHelper: TypeAlias = AbstractSiteHelper._ContentParserHelper
