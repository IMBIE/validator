# import pkgutil
from jinja2 import Environment, FileSystemLoader, select_autoescape
from dataclasses import dataclass
import datetime as dt
import os
from validator.const.basins import IceSheet

from validator.model.contribution import Contribution, Statistics
from validator.plot.contribution_plot import contribution_plot
from validator.report.util.load_image import load_image


@dataclass(frozen=True)
class SubmissionInfo:
    name: str
    institute: str
    group: str


@dataclass(frozen=True)
class Images:
    check: str
    cross: str
    gear: str


def render_report(contribution: Contribution) -> str:
    template_dir = os.path.dirname(__file__)
    env = Environment(
        loader=FileSystemLoader(template_dir), autoescape=select_autoescape()
    )
    template = env.get_template("template.html")

    stats: Statistics = contribution.get_stats()
    graph_image = contribution_plot(contribution)

    all_basins = [
        IceSheet.APIS,
        IceSheet.EAIS,
        IceSheet.WAIS,
        IceSheet.AIS,
        IceSheet.GRIS,
    ]
    basins_info = []
    for basin in all_basins:
        dmdt_series = contribution.filter(format="dmdt", basin_id=basin).first()
        dm_series = contribution.filter(format="dm", basin_id=basin).first()

        if dmdt_series is None and dm_series is not None:
            dmdt_series = dm_series.to_dmdt()
        elif dm_series is None and dmdt_series is not None:
            dm_series = dmdt_series.to_dm()

        dmdt_info = dmdt_series.get_statistics() if dmdt_series is not None else None
        dm_info = dm_series.get_statistics() if dm_series is not None else None

        basins_info.append({"basin": basin, "dmdt": dmdt_info, "dm": dm_info})

    imgs = Images(
        load_image("check.png"), load_image("cross.png"), load_image("gear.png")
    )

    return template.render(
        submission=contribution,
        graph=f"data:image/png;base64,{graph_image}",
        statistics=stats,
        basins=basins_info,
        images=imgs,
    )
