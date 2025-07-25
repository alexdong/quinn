from pathlib import Path
from unittest.mock import patch

from quinn.cli import _reset_all, _setup_database
from quinn.db.database import DATABASE_FILE
from quinn.db.conversations import ConversationStore
from quinn.db.messages import MessageStore
from quinn.db.users import UserStore
from quinn.models.conversation import Conversation
from quinn.models.message import Message


def test_reset_all(tmp_path: Path) -> None:
    db_file = tmp_path / "cli.db"
    with (
        patch("quinn.db.database.DATABASE_FILE", str(db_file)),
        patch("quinn.cli.DATABASE_FILE", str(db_file)),
    ):
        _setup_database()
        conv = Conversation(id="c1", user_id="cli-user")
        ConversationStore.create(conv)
        msg = Message(id="m1", conversation_id="c1", user_content="hi")
        MessageStore.create(msg, "cli-user")

        assert ConversationStore.get_by_id("c1") is not None
        assert MessageStore.get_by_id("m1") is not None

        _reset_all()

        assert ConversationStore.get_by_id("c1") is None
        assert MessageStore.get_by_id("m1") is None
        assert UserStore.get_by_email("cli@localhost") is not None
        assert db_file.exists()
