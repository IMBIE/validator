import base64
from dataclasses import dataclass
from fnmatch import fnmatch
import json
import os
from typing import Any, Dict, List

from validator.const.experiment_groups import ExperimentGroup

UPLOADS = {
    ExperimentGroup.gmb: [
        "time-series-upload",
        "mass-rate-upload",
        "methods-and-errors",
    ],
    ExperimentGroup.iom: [
        "time-series-discharge-upload",
        "time-series-surface-mass-balance-upload",
        "time-series-flux-gates-upload",
        "time-series-metadata-upload",
        "time-series-total-mass-change-upload",
        "discrete-rates-discharge-upload",
        "discrete-rates-surface-mass-balance-upload",
        "discrete-rates-flux-gates-upload",
        "discrete-rates-metadata-upload",
        "discrete-rates-total-mass-change-upload",
        "methods-and-errors",
    ],
    ExperimentGroup.ra: [
        "time-series-upload",
        "mean-rate-upload",
        "methods-and-errors",
    ],
    ExperimentGroup.gia: [
        "uplift-rates-data",
        "uplift-rates-meta",
        "stokes-coefficients-data",
        "stokes-coefficients-meta",
        "methods-and-errors",
    ],
    ExperimentGroup.smb: [
        "mass-balance-data",
        "mass-balance-meta",
        "gridded-mass-balance-data",
        "gridded-mass-balance-meta",
        "methods-and-errors",
    ],
}

FORMATS = {
    "time-series-upload": "dm",
    "mass-rate-upload": "dmdt",
    "mean-rate-upload": "dmdt",
    "time-series-discharge-upload": "dm",
    "time-series-surface-mass-balance-upload": "dm",
    "time-series-flux-gates-upload": "dm",
    "time-series-total-mass-change-upload": "dm",
    "discrete-rates-discharge-upload": "dmdt_iom",
    "discrete-rates-surface-mass-balance-upload": "dmdt_iom",
    "discrete-rates-flux-gates-upload": "dmdt_iom",
    "discrete-rates-total-mass-change-upload": "dmdt_iom",
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


def from_directory(dirpath: str) -> List[UnpackingRecord]:
    """
    get list of uploaded files from a previously
    unpacked submission
    """

    json_path = first_in_directory(dirpath, "*.json")
    with open(json_path) as json_file:
        data = json.load(json_file)

    group = ExperimentGroup.parse(data.get("group"))

    return [
        UnpackingRecord(
            first_in_directory(os.path.join(dirpath, fieldname)), fieldname, group
        )
        for fieldname in UPLOADS[group]
        if os.path.exists(os.path.join(dirpath, fieldname))
    ]


def unpack(filepath: str, outdir: str) -> List[UnpackingRecord]:
    """
    b64 decode data uploads from submission JSON
    """

    filename = os.path.basename(filepath).rstrip(".json")
    outroot = os.path.join(outdir, filename)

    os.makedirs(outroot)

    # print("reading", filepath)

    with open(filepath) as f:
        submission: Dict[str, Any] = json.load(f)

    group = ExperimentGroup.parse(submission.get("group"))

    unpacked_files = []

    # get file upload field names from group id

    for field in UPLOADS[group]:

        node = submission.get(field, {})

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

    json_outpath = os.path.join(outroot, f"{filename}.json")

    with open(json_outpath, "w") as f:
        json.dump(submission, f)

    return unpacked_files
