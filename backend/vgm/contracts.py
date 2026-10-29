from typing import Literal
import uuid

import pydantic


class Contract(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        extra="forbid", str_strip_whitespace=True
    )


class Credentials(Contract):
    username: str = pydantic.Field(
        min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_]+$"
    )
    password: str = pydantic.Field(min_length=10, max_length=128)

    @pydantic.field_validator("username")
    @classmethod
    def lowercase(cls, value):
        return value.lower()

    model_config = pydantic.ConfigDict(
        extra="forbid", str_strip_whitespace=False
    )


class Register(Credentials):
    display_name: str = pydantic.Field(min_length=1, max_length=60)

    @pydantic.field_validator("display_name")
    @classmethod
    def clean_name(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Display name cannot be blank")
        return value


class Token(Contract):
    token: str = pydantic.Field(min_length=1, max_length=256)


class Actor(Contract):
    actor_id: uuid.UUID


class Search(Actor):
    query: str = pydantic.Field(min_length=1, max_length=60)


class Profiles(Contract):
    ids: list[uuid.UUID] = pydantic.Field(max_length=100)


class ProfileUpdate(Contract):
    display_name: str = pydantic.Field(min_length=1, max_length=60)
    bio: str = pydantic.Field(default="", max_length=280)


class UpdateProfile(ProfileUpdate, Actor):
    pass


class OpenConversation(Actor):
    recipient_id: uuid.UUID


class MessageQuery(Actor):
    conversation_id: uuid.UUID
    before: int | None = pydantic.Field(default=None, gt=0)
    after: int | None = pydantic.Field(default=None, ge=0)
    limit: int = pydantic.Field(default=50, ge=1, le=100)

    @pydantic.model_validator(mode="after")
    def one_direction(self):
        if self.before is not None and self.after is not None:
            raise ValueError("Use either before or after, not both")
        return self


class MessageBody(Contract):
    client_id: uuid.UUID
    kind: Literal["text", "video"] = "text"
    text: str = pydantic.Field(default="", max_length=4000)
    url: str | None = pydantic.Field(default=None, max_length=2048)

    @pydantic.model_validator(mode="after")
    def content_required(self):
        if self.kind == "text" and (not self.text or self.url is not None):
            raise ValueError(
                "Text messages need text and cannot include a video URL"
            )
        if self.kind == "video" and not self.url:
            raise ValueError("Video messages need a video URL")
        return self


class Send(MessageBody, Actor):
    conversation_id: uuid.UUID


class Resolve(Contract):
    url: str = pydantic.Field(min_length=1, max_length=2048)
