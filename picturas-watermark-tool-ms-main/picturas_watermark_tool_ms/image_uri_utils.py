import base64
import io
from PIL import Image
import numpy as np

def data_uri_to_image_file(data_uri):
    """
    Convert a data URI to a Pillow Image with RGBA mode to preserve transparency.
    """
    header, encoded = data_uri.split(",", 1)
    image_data = base64.b64decode(encoded)
    image_file = io.BytesIO(image_data)
    return image_file

def data_uri_to_image_array(data_uri):
    """
    Convert a data URI to a NumPy array using Pillow.
    """
    image_file = data_uri_to_image_file(data_uri)
    pil_image = Image.open(image_file)
    pil_image.convert("RGBA")
    return np.array(pil_image)

def image_to_data_uri(image, format="PNG"):
    """
    Convert a Pillow Image to a data URI using the specified format (default PNG).
    """
    buffered = io.BytesIO()
    image.save(buffered, format=format)
    encoded_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
    mime_type = f"image/{format.lower()}"
    return f"data:{mime_type};base64,{encoded_image}"

def image_array_to_data_uri(image_array, format="PNG"):
    """
    Convert a NumPy image array to a data URI using the specified format (default PNG).
    """
    pil_image = Image.fromarray(image_array)
    # Ensure image has an alpha channel for transparency if needed
    if pil_image.mode != "RGBA":
        pil_image = pil_image.convert("RGBA")
    return image_to_data_uri(pil_image, format=format)
