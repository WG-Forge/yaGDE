from typing import *
import json
import struct
import asyncio as aio
import logging as log

from client.actions import *
from client.responses import *


def serialize_action(t: ActionType, action: Optional[Action] = None) -> bytes:
    """
    Serialize an action to bytes.
    The format is:
    4 bytes: action type
    4 bytes: length of the JSON data
    n bytes: JSON data in UTF-8
    """

    def dictify(value) -> dict:
        """
        Convert a namedtuple to a dict recursively.
        Remove nones.
        """
        if hasattr(value, "_asdict"):
            return {k: dictify(v) for k, v in
                    value._asdict().items() if v is not None}

        return value

    if action is not None:
        data = dictify(action)
        data = json.dumps(data).encode("utf-8")
    else:
        data = b''

    return struct.pack("<II", t, len(data)) + data


def deserialize_response_header(data: bytes) -> tuple[ResponseCode, int]:
    """
    Deserialize the header of a response.
    The format is:
    4 bytes: response code
    4 bytes: length of the JSON data
    """
    c, l = struct.unpack("<II", data)
    return ResponseCode(c), l


def deserialize_response_data(t: ActionType, data: bytes) -> ActionResponse | None:
    """
    Deserialize the data of a response.
    The format is:
    n bytes: JSON data in UTF-8
    """
    if len(data) == 0:
        return None

    data = data.decode("utf-8")
    data = json.loads(data)
    match t:
        case ProtocolAction.LOGIN:
            return LoginResponse.from_json(data)
        case ProtocolAction.MAP:
            return MapResponse.from_json(data)
        case ProtocolAction.GAME_STATE:
            return GameStateResponse.from_json(data)
        case ProtocolAction.GAME_ACTIONS:
            return GameActionsResponse.from_json(data)
        case _:
            raise ValueError(f"Unknown action type: {t}")


def deserialize_error_response(c: ResponseCode, data: bytes) -> ErrorResponse:
    """
    Deserialize the data of an error response.
    The format is:
    n bytes: JSON data in UTF-8
    """
    data = data.decode("utf-8")
    data = json.loads(data)

    return ErrorResponse(c, data["error_message"])


class Session:
    def __init__(self, addr: str, port: int):
        self.addr = addr
        self.port = port
        self.reader = None
        self.writer = None
        self.is_connected = False

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, tb):
        await self.disconnect()

    async def connect(self):
        if self.is_connected:
            raise RuntimeError("Already connected")

        self.reader, self.writer = await aio.open_connection(self.addr, self.port)
        self.is_connected = True

    async def disconnect(self):
        if not self.is_connected:
            raise RuntimeError("Not connected")

        self.writer.close()
        await self.writer.wait_closed()
        self.is_connected = False

    async def action(self, t: ActionType, action: Optional[Action] = None) -> ActionResponse | ErrorResponse:
        data = serialize_action(t, action)

        self.writer.write(data)
        await self.writer.drain()

        log.debug(f"Sent action {t.name} - {action}, encoded: {data}")

        header = await self.reader.readexactly(8)
        c, l = deserialize_response_header(header)

        log.debug(f"Received header: code {str(c)}, length {l}")

        data = await self.reader.readexactly(l)
        match c:
            case ResponseCode.OKEY:
                log.debug(f"Received response data: {data}")
                response = deserialize_response_data(t, data)
                log.debug(f"Deserialized response: {response}")
                return response
            case _:
                log.error(f"Received response data: {data}")
                response = deserialize_error_response(c, data)
                log.error(f"Deserialized response: {response}")
                return response

    async def login(self, action: LoginAction) -> LoginResponse | ErrorResponse:
        return await self.action(ProtocolAction.LOGIN, action)

    async def logout(self) -> None | ErrorResponse:
        return await self.action(ProtocolAction.LOGOUT)

    async def map(self) -> MapResponse | ErrorResponse:
        return await self.action(ProtocolAction.MAP)

    async def game_state(self) -> GameStateResponse | ErrorResponse:
        return await self.action(ProtocolAction.GAME_STATE)

    async def game_actions(self) -> GameActionsResponse | ErrorResponse:
        return await self.action(ProtocolAction.GAME_ACTIONS)

    async def turn(self) -> None | ErrorResponse:
        return await self.action(ProtocolAction.TURN)

    async def chat(self, action: ChatAction) -> None | ErrorResponse:
        return await self.action(GameAction.CHAT, action)

    async def move(self, action: MoveAction) -> None | ErrorResponse:
        return await self.action(GameAction.MOVE, action)

    async def shoot(self, action: ShootAction) -> None | ErrorResponse:
        return await self.action(GameAction.SHOOT, action)
