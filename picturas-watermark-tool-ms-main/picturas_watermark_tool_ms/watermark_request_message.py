from pydantic import BaseModel

from .core.messages.request_message import RequestMessage


class WatermarkParameters(BaseModel):
    messageId: str
    user_id: str
    project_id: str
    inputImageURI: str
    configValue: float 
    configColor: str # Not used in this tool

WatermarkRequestMessage = RequestMessage[WatermarkParameters]
