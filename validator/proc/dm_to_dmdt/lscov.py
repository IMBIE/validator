import numpy as np
from numpy.linalg import solve, qr, cholesky


def lscov(
    a: np.ndarray, b: np.ndarray, v: np.ndarray = None, dx: bool = False
) -> np.ndarray:
    """
    This is a python implementation of the matlab lscov function. This has been written based upon the matlab source
    code for lscov.m, which can be found here: http://opg1.ucsd.edu/~sio221/SIO_221A_2009/SIO_221_Data/Matlab5/Toolbox/matlab/matfun/lscov.m
    """

    m, n = a.shape
    if m < n:
        raise Exception(f"problem must be over-determined so that M > N. ({m}, {n})")
    if v is None:
        v = np.eye(m)

    if v.shape != (m, m):
        raise Exception("v must be a {0}-by-{0} matrix".format(m))

    qnull, r = qr(a, mode="complete")
    q = qnull[:, :n]
    r = r[:n, :n]

    qrem = qnull[:, n:]
    g = qrem.T.dot(v).dot(qrem)
    f = q.T.dot(v).dot(qrem)

    c = q.T.dot(b)
    d = qrem.T.dot(b)

    x = solve(r, (c - f.dot(solve(g, d))))

    # This was not required for merge_dM, and so has been removed as it has problems.
    if dx:
        u = cholesky(v).T
        z = solve(u, b)
        w = solve(u, a)
        mse = (z.T.dot(z) - x.T.dot(w.T.dot(z))) / (m - n)
        q, r = qr(w)
        ri = solve(r, np.eye(n)).T
        dx = np.sqrt(np.sum(ri * ri, axis=0) * mse).T

        return x, dx
    return x
