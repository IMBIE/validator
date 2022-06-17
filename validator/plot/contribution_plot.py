import base64
import io
from typing import Any
from validator.const.basins import IceSheet
from validator.model.contribution import Contribution

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from validator.model.series import Series

YLABELS = {"dm": "$dM (Gt)$", "dmdt": "$\\frac{dM}{dt} (Gt/y)$"}


def plot_single(
    ax: plt.Axes,
    x: np.ndarray,
    y: np.ndarray,
    yerr: np.ndarray,
    *,
    title: str = None,
    ylabel: str = None,
    xlabel: str = None,
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
    ax.fill_between(x, y - yerr, y + yerr, alpha=0.5, color=line.get_color())


def contribution_plot(contribution: Contribution):
    """
    plot all ice-sheet series in a contribution
    """

    data_file = io.BytesIO()
    sheets = [IceSheet.APIS, IceSheet.EAIS, IceSheet.WAIS, IceSheet.GRIS]

    sns.set(rc={"figure.dpi": 300, "savefig.dpi": 300})
    fig, axs = plt.subplots(2, 4)

    aspect = 9 / 16
    width_inches = 16
    height_inches = width_inches * aspect
    fig.set_size_inches(width_inches, height_inches)

    # dM plots
    for j, fmt in enumerate(["dm", "dmdt"]):
        for i, sheet in enumerate(sheets):
            series: Series = contribution.get(basin_id=sheet, format=fmt)

            ax: plt.Axes = axs[j, i]

            if j == 0:
                ax.set_title(sheet.value)
            else:
                ax.set_xlabel("Year")
            if i == 0:
                ax.set_ylabel(YLABELS[fmt])

            if series:
                x = series.data["date"]
                y = series.data[fmt]
                yerr = series.data[f"{fmt}_sd"]
                plot_single(ax, x, y, yerr)
            else:
                ax.set_xticks([], [])
                ax.set_yticks([], [])

    plt.savefig(data_file, bbox_inches="tight", format="png")
    data_file.seek(0)
    data_encoded = base64.b64encode(data_file.read()).decode()
    data_file.close()

    return data_encoded
