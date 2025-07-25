from pathlib import Path

from quinn.db.conversations import ConversationStore
from quinn.db.emails import EmailStore
from quinn.db.users import UserStore
from quinn.models.email import EmailDirection, EmailMessage
from quinn.models.conversation import Conversation
from quinn.models.user import User


def test_emails_create_and_get(clean_db: Path) -> None:
    user = User(id="u1", email_addresses=["a@example.com"])
    UserStore.create(user)
    conv = Conversation(id="conv1", user_id="u1")
    ConversationStore.create(conv)
    email = EmailMessage(
        id="<e1>",
        conversation_id="conv1",
        direction=EmailDirection.INBOUND,
        from_email="a@example.com",
        to=["b@example.com"],
        subject="hi",
        text="hello",
    )
    EmailStore.create(email)
    result = EmailStore.get_by_conversation("conv1")
    assert clean_db  # trigger fixture
    assert len(result) == 1
    assert result[0].id == "<e1>"
