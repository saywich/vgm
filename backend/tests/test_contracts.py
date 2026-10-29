import uuid

import pydantic
import pytest

from vgm import contracts


def test_password_whitespace_is_preserved():
    data = contracts.Credentials(
        username="PERSON", password="  long password  "
    )
    assert data.password == "  long password  "
    assert data.username == "person"


@pytest.mark.parametrize(
    "data", [
        {
            "kind": "text",
            "text": "  "
        },
        {
            "kind": "video",
            "text": "caption"
        },
        {
            "kind": "text",
            "text": "hi",
            "url": "https://example.com"
        },
        {
            "kind": "file",
            "text": "no"
        },
        {
            "kind": "text",
            "text": "x" * 4001
        },
    ]
)
def test_invalid_message_contract(data):
    with pytest.raises(pydantic.ValidationError):
        contracts.MessageBody(client_id=uuid.uuid4(), **data)


def test_cannot_inject_actor_via_message_body():
    with pytest.raises(pydantic.ValidationError):
        contracts.MessageBody(
            client_id=uuid.uuid4(), text="hi", actor_id=str(uuid.uuid4())
        )


def test_profile_and_signup_reject_blank_names():
    with pytest.raises(pydantic.ValidationError):
        contracts.ProfileUpdate(display_name="   ")
    with pytest.raises(pydantic.ValidationError):
        contracts.Register(
            username="user", password="longpassword", display_name="  "
        )


def test_pagination_limits():
    with pytest.raises(pydantic.ValidationError):
        contracts.MessageQuery(
            actor_id=uuid.uuid4(), conversation_id=uuid.uuid4(), limit=10000
        )
