import os
from base64 import b64encode
import pkgutil


def load_image(filename: str) -> str:
    """
    reads image and returns it as a b64 encoded string
    """

    data = pkgutil.get_data("validator.data.images", filename)
    b64 = b64encode(data).decode()

    _, ext = os.path.splitext(filename)
    ext = ext.lstrip(".")

    return f"data:image/{ext};base64,{b64}"
