from site_param_helper.base import AbstractSiteParamHelper
from site_param_helper.yourator import YouratorParamHelper as _YouratorParamHelper
from site_param_helper.ozf import OZFParamHelper as _OZFParamHelper
from site_param_helper.cakeresume import CakeresumeParamHelper as _CakeresumeParamHelper
from site_types import SiteType


class SiteParamHelperHandle:
    """
    HelperHandle class constructs a concrete AbstractSiteParamHelper.
    """

    def __init__(self) -> None:
        assert False, "HelperHandle is not constructible."

    @staticmethod
    def get(type: SiteType = SiteType.UNSUPPORTED) -> AbstractSiteParamHelper:
        if type == SiteType.YOURATOR:
            return _YouratorParamHelper()
        elif type == SiteType.OZF:
            return _OZFParamHelper()
        elif type == SiteType.CAKERESUME:
            return _CakeresumeParamHelper()
        assert False, "ERROR: Unsupport request type"
