"""Web-based interface for Quinn using FastHTML."""

import logging
import traceback

from fasthtml.common import (
    H1,
    H2,
    H3,
    A,
    Button,
    Div,
    Form,
    Head,
    Html,
    Link,
    Option,
    P,
    Script,
    Select,
    Small,
    Style,
    Table,
    Tbody,
    Td,
    Textarea,
    Th,
    Thead,
    Title,
    Tr,
    fast_app,
    serve,
)
from starlette.responses import HTMLResponse

from quinn.core.conversation_manager import ConversationManager
from quinn.core.database_manager import DatabaseManager
from quinn.models.message import Message
from quinn.utils.logging import get_logger, setup_logging

logger = get_logger(__name__)

# Constants
WEB_USER_ID = "web-user"
DEFAULT_MODEL = "claude-sonnet-4"
CONVERSATION_TITLE_MAX_LENGTH = 50
CONVERSATION_TITLE_TRUNCATE_LENGTH = 47

# Create FastHTML app
app, rt = fast_app(
    live=True,
    hdrs=(
        Link(
            rel="stylesheet",
            href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css",
        ),
        Script(
            src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"
        ),
        Style("""
            .conversation-card {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin-bottom: 1rem;
                transition: box-shadow 0.15s ease-in-out;
            }
            .conversation-card:hover {
                box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
            }
            .message-content {
                background-color: #f8f9fa;
                border-radius: 6px;
                padding: 1rem;
                margin: 0.5rem 0;
                white-space: pre-wrap;
                word-wrap: break-word;
            }
            .user-message {
                background-color: #e3f2fd;
                border-left: 4px solid #2196f3;
            }
            .assistant-message {
                background-color: #f1f8e9;
                border-left: 4px solid #4caf50;
            }
            .metadata {
                font-size: 0.875rem;
                color: #6c757d;
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 4px;
                padding: 0.5rem;
                margin-top: 0.5rem;
            }
            .spinner-border-sm {
                width: 1rem;
                height: 1rem;
            }
            .form-container {
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                padding: 2rem;
                margin-bottom: 2rem;
            }
            .conversation-list {
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                padding: 1.5rem;
            }
            .navbar-brand {
                font-weight: bold;
                font-size: 1.5rem;
            }
            .hero-section {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 3rem 0;
                margin-bottom: 2rem;
                border-radius: 12px;
            }
            .feature-card {
                background: white;
                border-radius: 8px;
                padding: 1.5rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 1rem;
                height: 100%;
            }
        """),
    ),
)


def render_page_header():  # noqa: ANN201
    """Render the page header with navigation."""
    return Div(
        # Navigation
        Div(
            Div(
                A(
                    "Quinn",
                    href="/",
                    cls="navbar-brand text-white text-decoration-none",
                ),
                Div(
                    A("New Conversation", href="/", cls="btn btn-outline-light me-2"),
                    A(
                        "Conversations",
                        href="/conversations",
                        cls="btn btn-outline-light me-2",
                    ),
                    A("Reset All", href="/reset", cls="btn btn-outline-danger"),
                    cls="d-flex",
                ),
                cls="container d-flex justify-content-between align-items-center",
            ),
            cls="navbar navbar-expand-lg",
            style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem 0;",
        )
    )


def render_hero_section():  # noqa: ANN201
    """Render the hero section for the home page."""
    return Div(
        Div(
            Div(
                Div(
                    H1("Quinn - Your AI Rubber Duck", cls="display-4 fw-bold mb-3"),
                    P(
                        "Quinn helps you solve problems through guided reflection and clarifying questions. "
                        "Like rubber duck debugging, but smarter and conversational.",
                        cls="lead mb-4",
                    ),
                    cls="col-lg-8",
                ),
                cls="row justify-content-center text-center",
            ),
            cls="container",
        ),
        cls="hero-section",
    )


def render_features():  # noqa: ANN201
    """Render feature cards."""
    return Div(
        H2("How Quinn Works", cls="text-center mb-4"),
        Div(
            Div(
                Div(
                    H3("🤔 Ask Questions", cls="h5 mb-3"),
                    P(
                        "Describe your problem or challenge. Quinn will ask targeted clarification questions "
                        "to understand your situation better.",
                        cls="text-muted",
                    ),
                    cls="feature-card",
                ),
                cls="col-md-4",
            ),
            Div(
                Div(
                    H3("💡 Discover Solutions", cls="h5 mb-3"),
                    P(
                        "Through structured conversation, Quinn guides you to discover your own solutions "
                        "rather than providing direct answers.",
                        cls="text-muted",
                    ),
                    cls="feature-card",
                ),
                cls="col-md-4",
            ),
            Div(
                Div(
                    H3("🎯 Take Action", cls="h5 mb-3"),
                    P(
                        "End each session with concrete next steps and clear decision criteria "
                        "to move forward with confidence.",
                        cls="text-muted",
                    ),
                    cls="feature-card",
                ),
                cls="col-md-4",
            ),
            cls="row",
        ),
        cls="container mb-5",
    )


def render_message_display(message: Message):  # noqa: ANN201
    """Render a message with proper formatting."""
    content_divs = []

    # User message
    if message.user_content:
        content_divs.append(
            Div(
                P("You:", cls="fw-bold mb-2 text-primary"),
                Div(message.user_content, cls="message-content user-message"),
                cls="mb-3",
            )
        )

    # Assistant message
    if message.assistant_content:
        content_divs.append(
            Div(
                P("Quinn:", cls="fw-bold mb-2 text-success"),
                Div(message.assistant_content, cls="message-content assistant-message"),
                cls="mb-3",
            )
        )

    # Metadata
    if message.metadata:
        metadata_text = (
            f"💰 Cost: ${message.metadata.cost_usd:.6f} | "
            f"🔢 Tokens: {message.metadata.tokens_used:,} | "
            f"⏱️ Response Time: {message.metadata.response_time_ms}ms | "
            f"🤖 Model: {message.metadata.model_used}"
        )
        content_divs.append(Div(metadata_text, cls="metadata"))

    return Div(*content_divs, cls="conversation-card p-3")


def render_model_selector(selected_model: str = DEFAULT_MODEL):  # noqa: ANN201
    """Render model selection dropdown."""
    available_models = ConversationManager.get_available_models()
    options = [
        Option(model, value=model, selected=(model == selected_model))
        for model in available_models
    ]
    return Select(*options, name="model", cls="form-select", required=True)


@rt("/")
def get_home():  # noqa: ANN201
    """Home page with new conversation form."""
    try:
        # Get recent conversation for continue option
        recent_conversation = ConversationManager.get_most_recent_conversation(
            WEB_USER_ID
        )

        continue_section = []
        if recent_conversation:
            continue_section = [
                Div(
                    H3("Continue Recent Conversation", cls="h5 mb-3"),
                    P(
                        f'Last conversation: "{recent_conversation.title}"',
                        cls="text-muted mb-3",
                    ),
                    A(
                        "Continue Conversation",
                        href=f"/conversation/{recent_conversation.id}",
                        cls="btn btn-success",
                    ),
                    cls="text-center mb-4",
                ),
                Div(cls="border-top my-4"),
            ]

        return Html(
            Head(
                Title("Quinn - AI Rubber Duck"),
            ),
            Div(
                render_page_header(),
                render_hero_section(),
                render_features(),
                # Main content
                Div(
                    Div(
                        # Continue conversation section
                        *continue_section,
                        # New conversation form
                        Div(
                            H3("Start New Conversation", cls="h5 mb-4"),
                            Form(
                                Div(
                                    Textarea(
                                        placeholder="Describe your problem, challenge, or question. Quinn will help you think through it with targeted questions...",
                                        name="user_input",
                                        cls="form-control",
                                        rows="6",
                                        required=True,
                                    ),
                                    cls="mb-3",
                                ),
                                Div(
                                    Div(
                                        Div("Choose AI Model:", cls="form-label"),
                                        render_model_selector(),
                                        cls="col-md-6",
                                    ),
                                    Div(
                                        Button(
                                            "Start Conversation",
                                            type="submit",
                                            cls="btn btn-primary btn-lg",
                                            style="margin-top: 2rem;",
                                        ),
                                        cls="col-md-6 d-flex align-items-end",
                                    ),
                                    cls="row",
                                ),
                                method="post",
                                action="/start",
                            ),
                            cls="form-container",
                        ),
                        cls="col-lg-8 mx-auto",
                    ),
                    cls="container",
                ),
                cls="min-vh-100",
                style="background-color: #f8f9fa;",
            ),
        )
    except Exception as e:
        logger.error("Error in home page: %s", e)
        logger.error("Traceback: %s", traceback.format_exc())
        return HTMLResponse("Internal Server Error", status_code=500)


@rt("/start", methods=["POST"])
async def post_start(user_input: str, model: str = DEFAULT_MODEL) -> HTMLResponse:
    """Start a new conversation."""
    try:
        if not user_input.strip():
            return HTMLResponse("User input is required", status_code=400)

        # Create new conversation
        response = await ConversationManager.create_new_conversation(
            WEB_USER_ID, user_input.strip(), model
        )

        # Redirect to conversation view
        return HTMLResponse(
            f'<script>window.location.href="/conversation/{response.conversation.id}";</script>',
            status_code=200,
        )

    except Exception as e:
        logger.error("Error starting conversation: %s", e)
        logger.error("Traceback: %s", traceback.format_exc())
        return HTMLResponse("Failed to start conversation", status_code=500)


@rt("/conversations")
def get_conversations():  # noqa: ANN201
    """List all conversations."""
    try:
        conversations = ConversationManager.list_conversations(WEB_USER_ID)

        if not conversations:
            conversation_content = [
                Div(
                    P("No conversations found.", cls="text-muted text-center"),
                    A("Start your first conversation", href="/", cls="btn btn-primary"),
                    cls="text-center py-5",
                )
            ]
        else:
            conversation_rows = []
            for i, conv in enumerate(conversations, 1):
                title = conv.title or "Untitled"
                if len(title) > CONVERSATION_TITLE_MAX_LENGTH:
                    title = title[:CONVERSATION_TITLE_TRUNCATE_LENGTH] + "..."

                conversation_rows.append(
                    Tr(
                        Td(str(i)),
                        Td(
                            A(
                                title,
                                href=f"/conversation/{conv.id}",
                                cls="text-decoration-none",
                            )
                        ),
                        Td(str(conv.message_count), cls="text-center"),
                        Td(f"${conv.total_cost:.6f}", cls="text-end"),
                        Td(conv.status),
                        Td(
                            conv.updated_at.strftime("%Y-%m-%d %H:%M"),
                            cls="text-muted small",
                        ),
                    )
                )

            conversation_content = [
                Table(
                    Thead(
                        Tr(
                            Th("#", scope="col"),
                            Th("Title", scope="col"),
                            Th("Messages", scope="col", cls="text-center"),
                            Th("Cost", scope="col", cls="text-end"),
                            Th("Status", scope="col"),
                            Th("Updated", scope="col"),
                        ),
                        cls="table-dark",
                    ),
                    Tbody(*conversation_rows),
                    cls="table table-hover",
                )
            ]

        return Html(
            Head(Title("Conversations - Quinn")),
            Div(
                render_page_header(),
                Div(
                    Div(
                        H1("Your Conversations", cls="mb-4"),
                        Div(*conversation_content, cls="conversation-list"),
                        cls="col-lg-10 mx-auto",
                    ),
                    cls="container py-4",
                ),
                cls="min-vh-100",
                style="background-color: #f8f9fa;",
            ),
        )

    except Exception as e:
        logger.error("Error listing conversations: %s", e)
        logger.error("Traceback: %s", traceback.format_exc())
        return HTMLResponse("Failed to load conversations", status_code=500)


@rt("/conversation/{conversation_id}")
def get_conversation(conversation_id: str):  # noqa: ANN201
    """View a specific conversation."""
    try:
        # Get conversation
        conversations = ConversationManager.list_conversations(WEB_USER_ID)
        conversation = next((c for c in conversations if c.id == conversation_id), None)

        if not conversation:
            return HTMLResponse("Conversation not found", status_code=404)

        # Get messages
        messages = ConversationManager.get_conversation_messages(conversation_id)

        # Render messages
        message_displays = [render_message_display(msg) for msg in messages]

        return Html(
            Head(Title(f"{conversation.title} - Quinn")),
            Div(
                render_page_header(),
                Div(
                    Div(
                        # Conversation header
                        Div(
                            H1(conversation.title, cls="mb-2"),
                            Small(
                                f"Messages: {conversation.message_count} | "
                                f"Total cost: ${conversation.total_cost:.6f} | "
                                f"Updated: {conversation.updated_at.strftime('%Y-%m-%d %H:%M')}",
                                cls="text-muted",
                            ),
                            cls="mb-4",
                        ),
                        # Messages
                        Div(*message_displays, cls="mb-4"),
                        # Continue conversation form
                        Div(
                            H3("Continue Conversation", cls="h5 mb-3"),
                            Form(
                                Div(
                                    Textarea(
                                        placeholder="Continue the conversation by answering Quinn's questions or adding more details...",
                                        name="user_input",
                                        cls="form-control",
                                        rows="4",
                                        required=True,
                                    ),
                                    cls="mb-3",
                                ),
                                Div(
                                    Div(
                                        Div("Choose AI Model:", cls="form-label"),
                                        render_model_selector(),
                                        cls="col-md-6",
                                    ),
                                    Div(
                                        Button(
                                            "Send Message",
                                            type="submit",
                                            cls="btn btn-success",
                                            style="margin-top: 2rem;",
                                        ),
                                        cls="col-md-6 d-flex align-items-end",
                                    ),
                                    cls="row",
                                ),
                                method="post",
                                action=f"/conversation/{conversation_id}/continue",
                            ),
                            cls="form-container",
                        ),
                        cls="col-lg-8 mx-auto",
                    ),
                    cls="container py-4",
                ),
                cls="min-vh-100",
                style="background-color: #f8f9fa;",
            ),
        )

    except Exception as e:
        logger.error("Error viewing conversation %s: %s", conversation_id, e)
        logger.error("Traceback: %s", traceback.format_exc())
        return HTMLResponse("Failed to load conversation", status_code=500)


@rt("/conversation/{conversation_id}/continue", methods=["POST"])
async def post_continue_conversation(
    conversation_id: str, user_input: str, model: str = DEFAULT_MODEL
) -> HTMLResponse:
    """Continue a conversation."""
    try:
        if not user_input.strip():
            return HTMLResponse("User input is required", status_code=400)

        # Check if conversation exists
        conversations = ConversationManager.list_conversations(WEB_USER_ID)
        conversation = next((c for c in conversations if c.id == conversation_id), None)

        if not conversation:
            return HTMLResponse("Conversation not found", status_code=404)

        # Continue conversation
        await ConversationManager.continue_conversation(
            conversation_id, WEB_USER_ID, user_input.strip(), model
        )

        # Redirect back to conversation view
        return HTMLResponse(
            f'<script>window.location.href="/conversation/{conversation_id}";</script>',
            status_code=200,
        )

    except Exception as e:
        logger.error("Error continuing conversation %s: %s", conversation_id, e)
        logger.error("Traceback: %s", traceback.format_exc())
        return HTMLResponse("Failed to continue conversation", status_code=500)


@rt("/reset")
def get_reset():  # noqa: ANN201
    """Reset all conversations (confirmation page)."""
    return Html(
        Head(Title("Reset All Conversations - Quinn")),
        Div(
            render_page_header(),
            Div(
                Div(
                    Div(
                        H1("Reset All Conversations", cls="mb-4 text-danger"),
                        P(
                            "This will permanently delete all conversations and cannot be undone.",
                            cls="alert alert-warning",
                        ),
                        Div(
                            A(
                                "Cancel",
                                href="/conversations",
                                cls="btn btn-secondary me-3",
                            ),
                            Form(
                                Button(
                                    "Reset All Conversations",
                                    type="submit",
                                    cls="btn btn-danger",
                                ),
                                method="post",
                                action="/reset",
                                style="display: inline;",
                            ),
                            cls="d-flex align-items-center",
                        ),
                        cls="text-center",
                    ),
                    cls="col-md-6 mx-auto",
                ),
                cls="container py-5",
            ),
            cls="min-vh-100",
            style="background-color: #f8f9fa;",
        ),
    )


@rt("/reset", methods=["POST"])
def post_reset() -> HTMLResponse:
    """Reset all conversations."""
    try:
        DatabaseManager.reset_all()
        DatabaseManager.ensure_web_user()

        return HTMLResponse(
            '<script>alert("All conversations have been reset."); window.location.href="/";</script>',
            status_code=200,
        )

    except Exception as e:
        logger.error("Error resetting conversations: %s", e)
        logger.error("Traceback: %s", traceback.format_exc())
        return HTMLResponse("Failed to reset conversations", status_code=500)


def main(
    host: str = "localhost",
    port: int = 8000,
    *,
    debug: bool = True,
    debug_modules: list[str] | None = None,
) -> None:
    """Run the Quinn web interface."""
    # Setup logging
    level = logging.DEBUG if debug else logging.INFO
    setup_logging(level=level, debug_modules=debug_modules)

    try:
        # Setup database
        DatabaseManager.setup_database()
        DatabaseManager.ensure_web_user()

        logger.info("Starting Quinn web interface on http://%s:%d", host, port)
        logger.info(
            "Available models: %s",
            ", ".join(ConversationManager.get_available_models()),
        )

        # Run the server
        serve(app=app, host=host, port=port)

    except Exception as e:
        logger.error("Failed to start web interface: %s", e)
        logger.error("Traceback: %s", traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
