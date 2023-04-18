from pathlib import Path
from site_helper import SiteHelperHandle
from jobs_integrator import JobsIntegrator
from site_types import SiteType
from datetime import datetime
import dcli

DEFAULT_OUTPUT = Path(__file__).parent.joinpath(
    "..", "data", f'jobs_{datetime.now().strftime("%Y-%m-%d")}.csv').resolve()
DEFAULT_FROM_DEST = Path(__file__).parent.joinpath(
    "..", "data", 'jobs.csv').resolve()
DEFAULT_SITES = set(filter(lambda t: t != SiteType.UNSUPPORTED, SiteType))
OPT_DEST = "out_dest"
OPT_KEYWORD = "keyword"
OPT_SITES = "opt_sites"
OPT_FROM_DEST = "from_dest"


OPT_FROM_SITES = set([])


def toSite(string: str):
    OPT_FROM_SITES.add(SiteType.cast(string))
    return string


@dcli.command(
    "fetch",
    dcli.arg(OPT_KEYWORD, metavar="SearchKeyword",
             help="specify the keyword for searching. [WIP]"),
    dcli.arg("-C", dest=OPT_DEST, action="store", type=Path, default=str(DEFAULT_OUTPUT),
             metavar="OutputPath",
             help="specify the destination to output the jobs information."),
    dcli.arg("-s", dest=OPT_SITES, type=toSite, default=None,
             choices=SiteType.getStrList(),
             help="specify the site to query."),
    dcli.arg("-f", dest=OPT_FROM_DEST, action="store", type=str, default=None,
             required=False,
             metavar="CombineFromPath",
             help="specify the destination to combine the fresh and history jobs information."),             
    help="fetch the job information from certain sites.",
    description="fetch the job information from certain sites."
)
def mrwooFetch(args):
    ARG_KEYWORD = getattr(args, OPT_KEYWORD)
    ARG_DEST = Path(getattr(args, OPT_DEST))
    ARG_SITES = OPT_FROM_SITES or DEFAULT_SITES

    if SiteType.UNSUPPORTED in ARG_SITES:
        print("ERROR: invalid type.")
        return 1

    integrator = JobsIntegrator()
    for site in ARG_SITES:
        print(f"requesting with keyword {ARG_KEYWORD} in |{site.name}|.")
        site_helper = SiteHelperHandle.get(site)
        integrator.add(site_helper.requestJobs(keyword = ARG_KEYWORD))

    if not ARG_DEST.parent.exists():
        ARG_DEST.parent.mkdir(exist_ok=True)

    integrator.export(ARG_DEST)

    if getattr(args, OPT_FROM_DEST):
        ARG_FROM_DEST = Path(getattr(args, OPT_FROM_DEST))
        integrator.upsert(ARG_FROM_DEST, ARG_DEST)
        integrator.export(ARG_FROM_DEST)

    return 0
