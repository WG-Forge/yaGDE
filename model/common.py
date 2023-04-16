from enum import Enum
from typing import *

from client.responses import MapContent as ResponseContent

PlayerId = NewType('PlayerId', int)


class Content(Enum):
    BASE = 0
    OBSTACLE = 1
    LIGHT_REPAIR = 2
    HARD_REPAIR = 3
    CATAPULT = 4

    @staticmethod
    def from_content_response(response: ResponseContent) -> 'Content':
        match response:
            case ResponseContent.BASE:
                return Content.BASE
            case ResponseContent.OBSTACLE:
                return Content.OBSTACLE
            case ResponseContent.LIGHT_REPAIR:
                return Content.LIGHT_REPAIR
            case ResponseContent.HARD_REPAIR:
                return Content.HARD_REPAIR
            case ResponseContent.CATAPULT:
                return Content.CATAPULT
            case _:
                raise ValueError(f"Unknown content response: {response}")
