from site_helper.base import AbstractSiteHelper
from site_helper.yourator import YouratorHelper as _YouratorHelper
from site_helper.ozf import OZFHelper as _OZFHelper
from site_helper.cakeresume import CakeresumeHelper as _CakeresumeHelper
from site_types import SiteType


class SiteHelperHandle:
    """
    HelperHandle class constructs a concrete AbstractSiteHelper.
    """

    def __init__(self) -> None:
        assert False, "HelperHandle is not constructible."

    @staticmethod
    def get(type: SiteType = SiteType.UNSUPPORTED) -> AbstractSiteHelper:
        if type == SiteType.YOURATOR:
            return _YouratorHelper()
        elif type == SiteType.OZF:
            return _OZFHelper()
        elif type == SiteType.CAKERESUME:
            return _CakeresumeHelper()
        assert False, "ERROR: Unsupport request type"
