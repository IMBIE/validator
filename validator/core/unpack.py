import base64
from dataclasses import dataclass
from fnmatch import fnmatch
import json
import os
import sys
from typing import Any, Dict, List

from validator.const.experiment_groups import ExperimentGroup

UPLOADS = {
    ExperimentGroup.GMB: [
        "time-series-upload",
        "mass-rate-upload",
        "methods-and-errors/upload",
    ],
    ExperimentGroup.IOM: [
        # "time-series-discharge-upload",
        # "time-series-surface-mass-balance-upload",
        # "time-series-flux-gates-upload",
        # "time-series-metadata-upload",
        "time-series-total-mass-change-upload",
        # "discrete-rates-discharge-upload",
        # "discrete-rates-surface-mass-balance-upload",
        # "discrete-rates-flux-gates-upload",
        # "discrete-rates-metadata-upload",
        "discrete-rates-total-mass-change-upload",
        "time-series-accumulation-upload",
        "methods-and-errors/upload",
    ],
    ExperimentGroup.RA: [
        "time-series-upload",
        "mean-rate-upload",
        "methods-and-errors/upload",
    ],
    ExperimentGroup.GIA: [
        "uplift-rates-data",
        "uplift-rates-meta",
        "stokes-coefficients-data",
        "stokes-coefficients-meta",
        "methods-and-errors/upload",
    ],
    ExperimentGroup.SMB: [
        "mass-balance-data",
        "mass-balance-meta",
        "gridded-mass-balance-data",
        "gridded-mass-balance-meta",
        "methods-and-errors/upload",
    ],
}

FORMATS = {
    "time-series-upload": "dm",
    "mass-rate-upload": "dmdt",
    "mean-rate-upload": "dmdt",
    # "time-series-discharge-upload": "dm",
    # "time-series-surface-mass-balance-upload": "dm",
    # "time-series-flux-gates-upload": "dm",
    "time-series-total-mass-change-upload": "dm",
    # "discrete-rates-discharge-upload": "iom-dmdt",
    # "discrete-rates-surface-mass-balance-upload": "iom-dmdt",
    # "discrete-rates-flux-gates-upload": "iom-dmdt",
    "discrete-rates-total-mass-change-upload": "dmdt",
    "time-series-accumulation-upload": "dmdt",
}


@dataclass(frozen=True)
class UnpackingRecord:
    filename: str
    fieldname: str
    group: ExperimentGroup

    @property
    def format_name(self) -> str:
        """
        get name of data format
        """
        return FORMATS[self.fieldname]


def first_in_directory(path: str, filter: str = None) -> str:
    """
    get first matching file in a directory
    """
    res, *_ = [
        os.path.join(path, fname)
        for fname in os.listdir(path)
        if filter is None or fnmatch(fname, filter)
    ]
    return res


def from_directory(dirpath: str, *, data_only: bool = False) -> List[UnpackingRecord]:
    """
    get list of uploaded files from a previously
    unpacked submission
    """

    json_path = first_in_directory(dirpath, "*.json")
    with open(json_path) as json_file:
        data = json.load(json_file)

    group = ExperimentGroup.parse(data.get("group"))

    is_data = (
        lambda fieldname: "methods-and-errors" not in fieldname
        and "flux-gates" not in fieldname
    )

    return [
        UnpackingRecord(
            first_in_directory(os.path.join(dirpath, fieldname)), fieldname, group
        )
        for fieldname in UPLOADS[group]
        if os.path.exists(os.path.join(dirpath, fieldname))
        and (not data_only or is_data(fieldname))
    ]


def unpack(
    filepath: str, outdir: str, *, strip: bool = False, data_only: bool = False
) -> List[UnpackingRecord]:
    """
    b64 decode data uploads from submission JSON
    """

    filename = os.path.basename(filepath).rstrip(".json")
    outroot = os.path.join(outdir, filename)

    os.makedirs(outroot)

    # print("reading", filepath)

    with open(filepath) as f:
        try:
            submission: Dict[str, Any] = json.load(f)
        except json.JSONDecodeError:
            sys.stderr.write(f"could not parse file: {filepath}\n")
            sys.exit(-1)

    group = ExperimentGroup.parse(submission.get("group"))

    unpacked_files = []

    # get file upload field names from group id

    for field in UPLOADS[group]:

        if not data_only and "methods-and-errors" in field:
            continue

        node = submission
        for part in field.split("/"):
            node = node.get(part, {})

        # node = submission.get(field, {})

        if not node.get("data"):
            continue

        # print(f"inflating field '{field}'", end="... ")
        # get original filename from json data
        dataname: str = node["name"]
        _, data = node.pop("data").split("base64,")

        outsubdir = os.path.join(outroot, field)
        os.makedirs(outsubdir, exist_ok=True)
        outpath = os.path.join(outsubdir, dataname)

        with open(outpath, "wb") as f:
            f.write(base64.b64decode(data, validate=True))
        unpacked_files.append(UnpackingRecord(outpath, field, group))

        if strip:
            first, *_ = field.split("/")
            del submission[first]

    json_outpath = os.path.join(outroot, f"{filename}.json")

    with open(json_outpath, "w") as f:
        json.dump(submission, f)

    return unpacked_files
