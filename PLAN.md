# Quinn Implementation Plan

## Overview

Quinn is an AI-powered email rubber duck that helps users solve problems through guided reflection and asking clarification questions. This plan outlines the complete implementation from scratch.

## Implementation Plan

### Phase 0: Implement the Prompts

By the end of this phase, we will have the initial prompts and follow-up questions ready for user interaction. All prompts will be tested and iterated upon to ensure they are effective in guiding users through their problem-solving process.

**Success Criteria:**
- Quinn consistently asks open-ended questions that guide discovery
- Quinn never provides direct solutions or answers
- Users report feeling like they discovered the solution themselves
- Prompts work effectively across technical, business, and personal problem domains

- [ ] Define prompt philosophy and testing approach
  - [ ] Create PROMPTS.md documenting the rubber duck methodology
  - [ ] Define example problem scenarios for testing (technical debugging, business decisions, personal challenges)
  - [ ] Create checklist for "good" rubber duck behavior
  - [ ] Document anti-patterns to avoid (being directive, solving problems, leading questions)

- [ ] Implement basic AI response generation using pydantic-ai
  - [ ] Create initial AI agent using pydantic-ai with Claude 3.5 Sonnet
  - [ ] Implement basic response generation logic with error handling
  - [ ] Add retry logic for API failures with exponential backoff
  - [ ] Implement cost tracking (tokens, API costs, response time) per interaction
  - [ ] Create fallback responses for API timeouts/failures

- [ ] Create conversation context management
  - [ ] Design SQLite schema: conversations, messages, metadata, prompt_versions
  - [ ] Create tables for: conversation_id, timestamp, prompt_version, tokens_used, cost, response_time, model_used
  - [ ] Implement basic CRUD operations for conversation management
  - [ ] Add in-memory storage backend for testing purposes
  - [ ] Create simple migration strategy for future schema changes
  - [ ] Implement session management with metadata tracking

- [ ] Create a CLI script that allows us to iterate on the prompts quickly
  - [ ] Create minimal CLI with two commands: `quinn prompt` (single test) and `quinn chat` (full conversation)
  - [ ] Add `--prompt-file` option to load prompts from external files
  - [ ] Add `--debug` flag to show costs/tokens/timing after each interaction
  - [ ] Create prompts/ directory with versioned files (v1_initial.txt, v1_clarification.txt, v1_followup.txt)
  - [ ] Implement prompt template variables: {{user_problem}}, {{previous_response}}, {{conversation_history}}
  - [ ] Add `--log-effectiveness` option to capture manual notes about prompt performance

- [ ] Develop core prompts through iterative testing
  - [ ] Create initial system prompt enforcing rubber duck methodology
  - [ ] Develop prompt for generating 5-7 clarification questions
  - [ ] Create follow-up prompt for after user answers questions
  - [ ] Design email footer with clear instructions and expectations
  - [ ] Test prompts with at least 10 different problem scenarios
  - [ ] Document prompt iterations and effectiveness in logs/


### Phase 1: End-to-End Functioning Agent using CLI

Create Quinn agent using pydantic-ai that can interact with users via a command-line interface (CLI). This will allow us to test the core functionality of the agent without needing a full web application or email processing system in place.

- `echo "User problem statement" | quinn -n` will start a new conversation with the given problem statement.
- `quinn` will start a new conversation or resume most recent conversation by opening up a temporary file using $EDITOR. 
- `quinn -l` will list all existing conversations where each conversation is identified by a unique int ID.
- `quinn -c N` will continue the conversation with ID N.

A few notes on the CLI:

1. It's critical that we can drop into any step of the conversation and continue from there.
2.  Keep in mind that we do not want to use the structured output just yet.

- [ ] Implement command-line interface using click
  - [ ] Handle user input and output formatting
  - [ ] Add basic error handling and logging

- [ ] Implement conversation state tracking
  - [ ] Create session model with thread_id as primary key
  - [ ] Store conversation history and context
  - [ ] Implement session expiration and cleanup
  - [ ] Response caching for common question patterns
  - [ ] Add privacy-preserving data retention policies

- [ ] Implement basic logging and tracing infrastructure

### Phase 2: Web Application

This phase will enable us to interact with Quinn via a single-user web application, allowing users to have conversations with the AI agent through a web interface. The web application will not handle email processing just yet. Basic administration features will be implemented to manage sessions and monitor usage.

Note that the web should be as minimum as possible. Think Craigslist-style. 

- [ ] Create FastHTML web application
  - [ ] Add a chat interface for user interaction
  - [ ] Display metadata like cost, response time etc as inline information
  - [ ] Implement message sending and receiving
  - [ ] Create conversation history view
  - [ ] Add health check and monitoring endpoints
  - [ ] Create admin interface for session viewing
  - [ ] Implement rate limiting and abuse prevention

- [ ] Implement Admin Interface
  - [ ] Create admin dashboard for session management
  - [ ] Add session statistics and analytics
  - [ ] Create user management interface for email allowlisting
  - [ ] Cost control and reporting features

- [ ] Add security features
  - [ ] Validate Postmark webhook signatures
  - [ ] Create audit logging for all interactions
  - [ ] Add an "allowlist" feature for email senders


### Phase 3: Email Processing System

The email thread reconstruction is achieved through the following steps:

1. Parse Message-ID from incoming email
2. Look up existing thread using In-Reply-To or References headers
3. Extract conversation history from thread
4. Identify new content vs quoted previous messages
5. Build context for AI agent with conversation flow

- [ ] Implement Postmark integration
  - [ ] Create email receiver webhook endpoint
  - [ ] Parse incoming email structure (headers, body, attachments)
  - [ ] Extract thread context and conversation history
  - [ ] Validate sender against allowed_email_addresses if configured

- [ ] Build email sender functionality
  - [ ] Create email formatter with proper headers
  - [ ] Implement thread-aware reply functionality
  - [ ] Add HTML/plain text dual format support
  - [ ] Handle email delivery errors and retries

- [ ] Implement email security features
  - [ ] Postmark webhook signature validation for all incoming requests
  - [ ] Optional email allowlisting for controlled access via config
  - [ ] Rate limiting per sender to prevent abuse
  - [ ] Audit logging for all security-relevant events

### Phase 4: Core Infrastructure Setup

- [ ] Create user configuration system
  - [ ] Each user can have more than one email address

- [ ] Allow the user to rate a response or interaction
  - [ ] Create a rating system for user feedback
  - [ ] Display the rating prompt in the email response footer
  - [ ] Store ratings in conversation metadata
  - [ ] Implement basic analytics dashboard for ratings

- [ ] Create project configuration system
  - [ ] Convert the `config.py` into config on per user basis

- [ ] Expand logging infrastructure
  - [ ] Create centralized logging configuration with proper levels
  - [ ] Implement trace_id/span_id generation for request tracking
  - [ ] Add debug module filtering support (--debug-modules)
  - [ ] Create log rotation and management utilities
  - [ ] Implement @functools.wraps decorators for tracing

## Directory Structure

Following Python.md conventions for one-person army readability:

```
./
├── quinn/                 # Main application package
│   ├── __init__.py
│   ├── web.py             # Top-level entry point for the web server
│   ├── cli.py             # CLI entry point for command-line interactions
│   ├── prompts.py         # Exercise individual prompts
│   ├── email_handler/
│   │   ├── __init__.py
│   │   ├── postmark.py    # Postmark API integration with extensive logging
│   │   ├── postmark_test.py
│   │   ├── parser.py      # Email parsing with raw email handling
│   │   ├── parser_test.py
│   │   ├── sender.py      # Email sending with retry logic
│   │   └── sender_test.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── prompts.py     # System prompts preventing direct solutions
│   │   ├── prompts_test.py
│   ├── scripts/           # Directory for various scripts
│   ├── session/
│   │   ├── __init__.py
│   │   ├── manager.py     # Session management with thread tracking
│   │   ├── manager_test.py
│   │   ├── storage.py     # Abstract storage interface
│   │   ├── storage_test.py
│   │   └── backends/
│   │       ├── __init__.py
│   │       ├── sqlite.py  # SQLite backend with raw SQL
│   │       ├── sqlite_test.py
│   ├── templates/
│   │   ├── __init__.py
│   │   └── prompts/
│   │       ├── __init__.py
│   │       ├── initial.j2
│   │       └── response.h2
│   │       └── footer.h2
│   ├── web/
│   │   ├── __init__.py
│   │   ├── admin.py       # FastHTML application with webhook endpoints
│   │   ├── admin_test.py
│   │   ├── app.py         # FastHTML application with webhook endpoints
│   │   ├── app_test.py
│   │   ├── webhooks.py    # Postmark webhook handlers
│   │   ├── webhooks_test.py
│   └── utils/
│       ├── __init__.py
│       ├── logging.py     # Centralized logging with trace_id/span_id
│       ├── logging_test.py
│       ├── tracing.py     # Request tracing utilities
│       └── tracing_test.py
├── tests/
│   ├── integration/       # Cross-component integration tests
│   │   ├── __init__.py
│   │   ├── email_flow_test.py
│   │   └── conversation_test.py
│   └── e2e/              # End-to-end system tests
│       ├── __init__.py
│       ├── full_session_test.py
│       └── performance_test.py
├── logs/                 # Implementation logs per Python.md
├── docs/                 # Documentation
├── llms/                 # Third-party tools documentation
├── pyproject.toml        # Project configuration with uv
├── config.toml           # Runtime configuration template
├── Makefile              # Enhanced with Quinn-specific targets
├── README.md             # Project README
└── CLAUDE.md             # Claude Code instructions
```