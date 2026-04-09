from typing import Any, Dict, Literal, Union, List, Annotated
from pydantic import BaseModel, Field


class BaseMessage(BaseModel):
    type: str


class PlayerStateData(BaseModel):
    # This could contain a base64 string or an array of transform matrices.
    # To keep it flexible for the C++ side using simdjson, we'll allow an arbitrary dict or list.
    transforms: Any = Field(
        description="Character transform matrices or positional properties"
    )


class PlayerStateMessage(BaseMessage):
    type: Literal["state"] = "state"
    client_id: int | None = None
    data: PlayerStateData


class ChatMessage(BaseMessage):
    type: Literal["chat"] = "chat"
    client_id: int | None = None
    sender: str = ""
    text: str


class BlockUpdateMessage(BaseMessage):
    type: Literal["block"] = "block"
    client_id: int | None = None
    x: int
    y: int
    z: int
    mat_id: int


# Discriminated union for parsing incoming websocket messages
ClientMessage = Annotated[
    Union[PlayerStateMessage, ChatMessage, BlockUpdateMessage],
    Field(discriminator="type"),
]


class ServerStateBroadcast(BaseModel):
    type: Literal["broadcast"] = "broadcast"
    players: Dict[int, PlayerStateData]


class ServerInitMessage(BaseModel):
    type: Literal["init"] = "init"
    client_id: int
    max_players: int
