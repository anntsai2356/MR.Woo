from site_param_helper.base import AbstractSiteParamHelper as _AbstractSiteParamHelper


class CakeresumeParamHelper(_AbstractSiteParamHelper):
    def __init__(self) -> None:
        self._param_name_mapping: dict = {
            "keyword": "query",
        }
