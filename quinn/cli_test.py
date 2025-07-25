from pathlib import Path
from unittest.mock import patch

from quinn.cli import _reset_all, _setup_database
from quinn.db.conversations import Conversations, DbConversation
from quinn.db.messages import Messages
from quinn.db.users import Users
from quinn.models.message import Message


def test_reset_all(tmp_path: Path) -> None:
    db_file = tmp_path / "cli.db"
    with (
        patch("quinn.db.database.DATABASE_FILE", str(db_file)),
        patch("quinn.cli.DATABASE_FILE", str(db_file)),
    ):
        _setup_database()
        conv = DbConversation(conversation_id="c1", user_id="cli-user")
        Conversations.create(conv)
        msg = Message(id="m1", conversation_id="c1", user_content="hi")
        Messages.create(msg, "cli-user")

        assert Conversations.get_by_id("c1") is not None
        assert Messages.get_by_id("m1") is not None

        _reset_all()

        assert Conversations.get_by_id("c1") is None
        assert Messages.get_by_id("m1") is None
        assert Users.get_by_id("cli-user") is not None
        assert db_file.exists()
