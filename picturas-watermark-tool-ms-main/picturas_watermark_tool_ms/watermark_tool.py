import json
import random
import string

from PIL import Image, ImageEnhance

from .core.tool import Tool
from .watermark_request_message import WatermarkParameters
from .image_uri_utils import data_uri_to_image_file, image_to_data_uri

class WatermarkTool(Tool):

    def __init__(
        self,
        watermark_image_path: str,
        opacity: float = 0.7,
    ) -> None:
        """
        Initialize the WatermarkTool with the path to the watermark image.

        Args:
            watermark_image_path (str): Path to the watermark image.
            opacity (float): Transparency level of the watermark (0.0 to 1.0).
        """
        self.watermark_image = Image.open(watermark_image_path).convert("RGBA")
        self.opacity = opacity

    def _apply_opacity(self, image: Image.Image) -> Image.Image:
        alpha = image.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(self.opacity)
        image.putalpha(alpha)
        return image

    def apply(self, parameters: WatermarkParameters):
        """
        Apply the watermark with an overlay effect to the input image and save the result.

        Args:
            parameters (WatermarkParameters): watermark parameters.
        """
        try:
            user_id = parameters["user_id"]
            project_id = parameters["project_id"]
            input_image_uri = parameters["inputImageURI"]
            self.opacity = parameters.get("configValue", 0.7)

            # Convert input URI to PIL image
            img = data_uri_to_image_file(input_image_uri)
        
            # Open the input image
            input_image = Image.open(img).convert("RGBA")

            # Resize and adjust the watermark's opacity
            watermark = self.watermark_image.copy()

            # Scale watermark to fit the smallest dimension of the input image
            # Set watermark size to 30% of the smallest dimension
            smallest_dimension = min(input_image.size)
            scale_factor = smallest_dimension * 0.3
            new_watermark_size = (
                int(watermark.size[0] * scale_factor / smallest_dimension),
                int(watermark.size[1] * scale_factor / smallest_dimension),
            )
            watermark = watermark.resize(new_watermark_size)
            watermark = self._apply_opacity(watermark)

            # Generate random position for the watermark
            random_x = random.randint(0, max(0, input_image.size[0] - new_watermark_size[0]))
            random_y = random.randint(0, max(0, input_image.size[1] - new_watermark_size[1]))
            watermark_position = (random_x, random_y)

            # Create a transparent overlay
            overlay = Image.new("RGBA", input_image.size, (0, 0, 0, 0))
            overlay.paste(watermark, watermark_position, mask=watermark)

            # Blend the input image and the overlay
            blended_image = Image.alpha_composite(input_image, overlay)

            # Save the final image
            # Convert back to RGB for saving
            final_image = blended_image.convert("RGB")
            # Convert the output to URI
            output_uri = image_to_data_uri(final_image)

            # Success response
            response = {
                "messageId": ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(32)),
                "user_id": user_id,
                "project_id": project_id,
                "status": "success",
                "error": {},
                "output": {
                    "type": "image",
                    "imageURI": output_uri,
                },
                "metadata": {
                    "microservice": "WatermarkTool"
                }
            }
        except Exception as e:
            # Error response
            response = {
                "messageId": ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(32)),
                "user_id": parameters.get("user_id", "unknown"),
                "project_id": parameters.get("project_id", "unknown"),
                "status": "error",
                "error": {
                    "code": "INVALID_INPUT",
                    "message": str(e),
                    "details": {
                        "inputFileURI": parameters.get("inputImageURI", "unknown")
                    }
                },
                "output": {},
                "metadata": {
                    "microservice": "WatermarkTool"
                }
            }
        return json.dumps(response)