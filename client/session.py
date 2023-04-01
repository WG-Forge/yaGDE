from typing import *
import socket
import json
import struct
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
        self.server_addr = (addr, port)
        self.sock = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.disconnect()

    def connect(self):
        if self.sock is not None:
            raise RuntimeError("Already connected")

        self.sock = socket.create_connection(self.server_addr)

    def disconnect(self):
        if self.sock is None:
            raise RuntimeError("Not connected")

        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self.sock = None

    def action(self, t: ActionType, action: Optional[Action] = None) -> ActionResponse | ErrorResponse:
        data = serialize_action(t, action)
        self._sendall(data)
        log.debug(f"Sent action {str(t)} - {action}, encoded: {data}")
        header = self._recvall(8)
        c, l = deserialize_response_header(header)
        log.debug(f"Received header: code {str(c)}, length {l}")
        data = self._recvall(l)
        match c:
            case ResponseCode.OKEY:
                response = deserialize_response_data(t, data)
                log.debug(f"Received response: {response}")
                return response
            case _:
                response = deserialize_error_response(c, data)
                log.error(f"Received error response: {response}")
                return response

    def login(self, action: LoginAction) -> LoginResponse | ErrorResponse:
        return self.action(ProtocolAction.LOGIN, action)

    def logout(self) -> None | ErrorResponse:
        return self.action(ProtocolAction.LOGOUT)

    def map(self) -> MapResponse | ErrorResponse:
        return self.action(ProtocolAction.MAP)

    def game_state(self) -> GameStateResponse | ErrorResponse:
        return self.action(ProtocolAction.GAME_STATE)

    def game_actions(self) -> GameActionsResponse | ErrorResponse:
        return self.action(ProtocolAction.GAME_ACTIONS)

    def turn(self) -> None | ErrorResponse:
        return self.action(ProtocolAction.TURN)

    def chat(self, action: ChatAction) -> None | ErrorResponse:
        return self.action(GameAction.CHAT, action)

    def move(self, action: MoveAction) -> None | ErrorResponse:
        return self.action(GameAction.MOVE, action)

    def shoot(self, action: ShootAction) -> None | ErrorResponse:
        return self.action(GameAction.SHOOT, action)

    def _sendall(self, data: bytes) -> None:
        self.sock.sendall(data)

    def _recvall(self, n: int) -> bytes:
        data = b''
        while len(data) < n:
            packet = self.sock.recv(n - len(data))
            if not packet:
                raise RuntimeError("Socket connection broken")
            data += packet
        return data
