import numpy as np


def dmdt_to_dm(
    t: np.ndarray, dmdt: np.ndarray, dmdt_sd: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    convert dmdt time series to dm
    """

    dm = np.cumsum()
