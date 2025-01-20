from typing import Any

from pydantic import BaseModel

from .core.messages.result_message import ResultMessage
from .watermark_request_message import WatermarkRequestMessage


class WatermarkResultOutput(BaseModel):
    messageId: str
    user_id: str
    project_id: str
    status: str
    error: dict
    output: dict
    metadata: dict


class WatermarkResultMessage(ResultMessage[WatermarkResultOutput]):

    def __init__(self, request: WatermarkRequestMessage, tool_result: Any, exception: Exception, *args):
        super().__init__(request, tool_result, exception, *args)
        if exception is None:
            self.output = WatermarkResultOutput(
                messageId=tool_result["messageId"],
                user_id=tool_result["user_id"],
                project_id=tool_result["project_id"],
                status=tool_result["status"],
                error=tool_result.get("error", {}),
                output=tool_result.get("output", {}),
                metadata=tool_result["metadata"]
            )
