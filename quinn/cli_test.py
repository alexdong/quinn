from pathlib import Path
from unittest.mock import patch

from quinn.cli import _reset_all, _setup_database, _get_last_assistant_message, _format_message_for_editor
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


def test_get_last_assistant_message(tmp_path: Path) -> None:
    """Test getting the last assistant message from a conversation."""
    db_file = tmp_path / "cli.db"
    with (
        patch("quinn.db.database.DATABASE_FILE", str(db_file)),
        patch("quinn.cli.DATABASE_FILE", str(db_file)),
    ):
        _setup_database()
        
        # Test with empty conversation
        assert _get_last_assistant_message("nonexistent") is None
        
        # Create conversation with messages
        conv = Conversation(id="c1", user_id="cli-user")
        ConversationStore.create(conv)
        
        # Add first message
        msg1 = Message(
            id="m1", 
            conversation_id="c1", 
            user_content="First question",
            assistant_content="First response"
        )
        MessageStore.create(msg1, "cli-user")
        
        # Add second message  
        msg2 = Message(
            id="m2",
            conversation_id="c1",
            user_content="Second question", 
            assistant_content="Second response"
        )
        MessageStore.create(msg2, "cli-user")
        
        # Should return the most recent assistant message
        result = _get_last_assistant_message("c1")
        assert result == "Second response"
        
        # Test with message having no assistant content
        msg3 = Message(
            id="m3",
            conversation_id="c1", 
            user_content="Third question",
            assistant_content=""
        )
        MessageStore.create(msg3, "cli-user")
        
        result = _get_last_assistant_message("c1")
        assert result is None


def test_format_message_for_editor() -> None:
    """Test formatting message content with line breaks at column 88 and '> ' prefix."""
    # Test single line (short)
    single_line = "This is a single line message"
    result = _format_message_for_editor(single_line)
    assert result == "> This is a single line message"
    
    # Test multiple paragraphs
    multi_line = "Line 1\nLine 2\nLine 3"
    expected = "> Line 1\n> Line 2\n> Line 3"
    result = _format_message_for_editor(multi_line)
    assert result == expected
    
    # Test empty lines (preserved as empty paragraphs)
    with_empty = "Line 1\n\nLine 3"
    expected_empty = "> Line 1\n> \n> Line 3"
    result = _format_message_for_editor(with_empty)
    assert result == expected_empty
    
    # Test empty string
    empty = ""
    result = _format_message_for_editor(empty)
    assert result == "> "
    
    # Test long line that needs wrapping (> 86 chars after prefix)
    long_line = "This is a very long line that should be wrapped at column 88 when prefixed with '> ' so that the total line length does not exceed 88 characters per line"
    result = _format_message_for_editor(long_line)
    lines = result.split('\n')
    
    # Check that all lines start with "> "
    for line in lines:
        assert line.startswith("> ")
    
    # Check that no line exceeds 88 characters total
    for line in lines:
        assert len(line) <= 88, f"Line too long: {len(line)} chars: {line}"
    
    # Check that the content is preserved when we remove prefixes and join
    content_only = '\n'.join(line[2:] for line in lines)
    reconstructed = ' '.join(content_only.split())  # Join wrapped lines
    original_normalized = ' '.join(long_line.split())  # Normalize spaces
    assert reconstructed == original_normalized
    
    # Test paragraph with multiple sentences
    paragraph = "First sentence here. Second sentence follows. Third sentence concludes the paragraph with some additional text to make it long enough for wrapping."
    result = _format_message_for_editor(paragraph)
    lines = result.split('\n')
    
    # Should be wrapped into multiple lines
    assert len(lines) > 1
    for line in lines:
        assert line.startswith("> ")
        assert len(line) <= 88
