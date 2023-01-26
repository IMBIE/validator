import base64
import io
from typing import Any
from validator.const.basins import IceSheet
from validator.const.experiment_groups import ExperimentGroup
from validator.model.contribution import Contribution

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from validator.model.series import Series

YLABELS = {
    "dm": "$dM (Gt)$",
    "dmdt": "$\\frac{dM}{dt} (Gt/y)$",
}


def plot_single(
    ax: plt.Axes,
    x: np.ndarray,
    y: np.ndarray,
    yerr: np.ndarray,
    *,
    title: str = None,
    ylabel: str = None,
    xlabel: str = None,
    fill: bool = True,
    **style_opts: Any,
) -> None:
    """
    plot a single dataseries on a given matplotlib Axes object.
    Optionally sets title and axes labels
    """
    if title is not None:
        ax.set_title(title)
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)

    line, *_ = ax.errorbar(x, y, yerr=yerr, **style_opts)
    if fill:
        ax.fill_between(x, y - yerr, y + yerr, alpha=0.5, color=line.get_color())


def plot_single_dmdt(
    ax: plt.Axes,
    x0: np.ndarray,
    x1: np.ndarray,
    y: np.ndarray,
    yerr: np.ndarray,
    **kwargs,
) -> None:
    """
    plot a single dm/dt contribution
    """
    for i, yval in enumerate(y):
        plot_single(
            ax,
            np.asarray([x0[i], x1[i]]),
            np.asarray([yval, yval]),
            np.asarray([yerr[i], yerr[i]]),
            **kwargs,
        )


def contribution_plot(contribution: Contribution):
    """
    plot all ice-sheet series in a contribution
    """

    data_file = io.BytesIO()
    sheets = [IceSheet.APIS, IceSheet.EAIS, IceSheet.WAIS, IceSheet.GRIS]

    col = {
        ExperimentGroup.GMB: "green",
        ExperimentGroup.RA: "red",
        ExperimentGroup.IOM: "blue",
    }.get(contribution.experiment_group, "gray")

    sns.set(rc={"figure.dpi": 300, "savefig.dpi": 300})
    fig, axs = plt.subplots(2, 4)

    aspect = 9 / 16
    width_inches = 16
    height_inches = width_inches * aspect
    fig.set_size_inches(width_inches, height_inches)

    # dmdt_fmt_query = (
    #     "iom-dmdt" if contribution.experiment_group == ExperimentGroup.IOM else "dmdt"
    # )
    dmdt_fmt_query = "dmdt"

    # dM plots
    for j, fmt in enumerate(["dm", "dmdt"]):
        for i, sheet in enumerate(sheets):
            fmt_query = dmdt_fmt_query if fmt == "dmdt" else fmt
            series: Series = contribution.get(basin_id=sheet, format=fmt_query)

            if series is None:
                if fmt == "dm":
                    dmdt_series = contribution.get(
                        basin_id=sheet, format=dmdt_fmt_query
                    )
                    if dmdt_series is not None:
                        series = dmdt_series.to_dm()
                    else:
                        series = None
                else:
                    dm_series = contribution.get(basin_id=sheet, format="dm")
                    if dm_series is not None:
                        series = dm_series.to_dmdt()
                    else:
                        series = None
                computed = True
            else:
                computed = False

            ax: plt.Axes = axs[j, i]

            if j == 0:
                ax.set_title(sheet.value)
            else:
                ax.set_xlabel("Year")
            if i == 0:
                ax.set_ylabel(YLABELS[fmt])

            if series:
                if "date_0" in series.data.columns:
                    x0 = series.data["date_0"].values
                    x1 = series.data["date_1"].values
                    y = series.data["dmdt"].values
                    yerr = series.data["dmdt_sd"].values

                    plot_single_dmdt(ax, x0, x1, y, yerr, color=col)
                else:
                    x = series.data["date"]
                    y = series.data[fmt]
                    yerr = series.data[f"{fmt}_sd"]
                    plot_single(ax, x, y, yerr, color=col)
                ymin, ymax = ax.get_ylim()
                yrange = ymax - ymin

                min_yrange = 10 * np.nanmean(series.data[f"{fmt}_sd"])
                if yrange < min_yrange:
                    ymid = (ymax + ymin) / 2
                    ymin = ymid - (min_yrange / 2)
                    ymax = ymid + (min_yrange / 2)

                    if np.isfinite([ymin, ymax]).all():
                        ax.set_ylim(ymin, ymax)
                ax.axhline(0, color="gray", ls="-", lw=2)
            else:
                ax.set_xticks([], [])
                ax.set_yticks([], [])

    plt.savefig(data_file, bbox_inches="tight", format="png")
    data_file.seek(0)
    data_encoded = base64.b64encode(data_file.read()).decode()
    data_file.close()

    return data_encoded
