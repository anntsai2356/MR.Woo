from enum import Enum


class SiteType(Enum):
    UNSUPPORTED = -1
    OZF = 0
    YOURATOR = 1
    CAKERESUME = 2

    @staticmethod
    def validSites():
        return list(filter(lambda t: t != SiteType.UNSUPPORTED, SiteType))

    @staticmethod
    def getStrList():
        return [e.name.lower() for e in filter(lambda t: t != SiteType.UNSUPPORTED, SiteType)]

    @staticmethod
    def cast(name: str):
        if name.lower() not in SiteType.getStrList():
            return SiteType.UNSUPPORTED
        return SiteType[name.upper()]
