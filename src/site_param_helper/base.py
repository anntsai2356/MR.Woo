from abc import ABC, abstractmethod
from urllib.parse import urlencode as _urlEncode


class AbstractSiteParamHelper(ABC):
    """
    AbstractSiteParamHelper class is a virtual class that provides some implementations
    about parameters in url query string

    DerivedHelper should set the mapping in variable "_param_name_mapping" by itself in __init__()
    """

    _param_name_mapping: dict = {}

    def __init__(self) -> None:
        pass

    def getValidParams(self, **params: dict) -> dict:
        valid_params = {}
        for key, value in params.items():
            if key not in self._param_name_mapping.keys():
                print(f"WARN: Not valid parameters. ({key} = {value})")
                continue

            valid_params[self._param_name_mapping[key]] = value

        return valid_params

    def getQuery(self, **kwargs) -> dict:
        return self.getValidParams(**kwargs)

    def getQueryString(self, **kwargs) -> str:
        valid_params = self.getValidParams(**kwargs)

        return _urlEncode(valid_params)
