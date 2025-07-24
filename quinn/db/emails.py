"""Database access for storing email messages."""

import json
import logging
from datetime import UTC, datetime

from quinn.db.database import get_db_connection
from quinn.models.email import EmailDirection, EmailMessage

logger = logging.getLogger(__name__)


class EmailStore:
    """CRUD helpers for the ``emails`` table."""

    @staticmethod
    def create(email: EmailMessage) -> None:
        """Insert an email into the database."""
        logger.info(
            "Storing email: id=%s conversation_id=%s direction=%s",
            email.id,
            email.conversation_id,
            email.direction.value,
        )
        with get_db_connection() as conn:
            cursor = conn.cursor()
            sql = """
                INSERT INTO emails (
                    id, conversation_id, created_at, direction,
                    from_email, to_addrs, cc_addrs, bcc_addrs,
                    subject, text, html, headers
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                email.id,
                email.conversation_id,
                int(email.created_at.timestamp()),
                email.direction.value,
                email.from_email,
                json.dumps(email.to),
                json.dumps(email.cc),
                json.dumps(email.bcc),
                email.subject,
                email.text,
                email.html,
                json.dumps(email.headers),
            )
            logger.info("SQL: %s | Params: %s", sql.strip(), params)
            cursor.execute(sql, params)
            assert cursor.rowcount == 1, (
                f"Failed to insert email {email.id}: {cursor.rowcount} rows"
            )
            conn.commit()

    @staticmethod
    def get_by_conversation(conversation_id: str) -> list[EmailMessage]:
        """Retrieve all emails for a conversation."""
        logger.debug("Loading emails for conversation %s", conversation_id)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            sql = "SELECT * FROM emails WHERE conversation_id = ? ORDER BY created_at"
            params = (conversation_id,)
            logger.info("SQL: %s | Params: %s", sql, params)
            cursor.execute(sql, params)
            rows = cursor.fetchall()
        return [
            EmailMessage(
                id=row[0],
                conversation_id=row[1],
                created_at=datetime.fromtimestamp(row[2], UTC),
                direction=EmailDirection(row[3]),
                from_email=row[4],
                to=json.loads(row[5]),
                cc=json.loads(row[6]),
                bcc=json.loads(row[7]),
                subject=row[8],
                text=row[9],
                html=row[10],
                headers=json.loads(row[11]) if row[11] else {},
            )
            for row in rows
        ]


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    from quinn.models.email import EmailMessage

    sample = EmailMessage(
        id="<demo>",
        conversation_id="demo-conv",
        from_email="alice@example.com",
        to=["bob@example.com"],
        subject="Hello",
        text="Just a demo",
    )
    EmailStore.create(sample)
    print(EmailStore.get_by_conversation("demo-conv"))
