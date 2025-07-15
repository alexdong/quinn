# Quinn Implementation Plan

## Overview

Quinn is an email-native, AI-powered “rubber duck.” It guides technically‑oriented users to solve their own problems by asking clarifying questions, prompting structured self‑explanation, and—when warranted—convening an independent **panel** of perspectives. Quinn is a facilitator, not an oracle.

### Representative Use Cases

* **Technical Architecture Trade‑off:** Choosing an authentication and user account management system for a new web application.
* **Life Choices & Decision:** How to help a 11-year-old daughter to decide if she should drop ballet next term.
* **Value‑Based Consulting Quote:** Pricing a 10–20‑hour, expertise‑heavy engagement that requires substantial background preparation, research and thinking.

## Implementation Plan

### Phase 0: Implement the Prompts

By the end of this phase, we will have the initial prompts and follow-up questions ready for user interaction. All prompts will be tested and iterated upon to ensure they are effective in guiding users through their problem-solving process.

**Success Criteria:**
- Quinn consistently asks open-ended questions that guide discovery
- Quinn never provides direct solutions or answers
- Users report feeling like they discovered the solution themselves
- Prompts work effectively across technical, business, and personal problem domains

1. [x] Define prompt philosophy and testing approach
  1. [x] Create METHODOLOGY.md documenting the rubber duck methodology
  2. [x] Create checklist for "good" rubber duck behavior
  3. [x] Document anti-patterns to avoid (being directive, solving problems, leading questions)

2. [x] Implement basic AI response generation using pydantic-ai (API documentation is avaiable at ./llms/pydantic-ai.md)
  1. [x] Create initial AI agent using pydantic-ai with Claude 4.0 Sonnet
  2. [x] Implement basic response generation logic with error handling
  3. [x] Add retry logic for API failures with exponential backoff
  4. [x] Implement cost tracking (tokens, API costs, response time) per interaction
  5. [x] Create comprehensive Quinn rubber duck system prompt based on METHODOLOGY.md
  6. [x] Fix failing integration tests and ensure full end-to-end functionality
  7. [x] Test that Quinn actually behaves as rubber duck (asks questions, doesn't give solutions)
  8. [x] Verify error handling works correctly for API failures, network issues, invalid inputs
  9. [x] Validate cost calculations match actual API pricing and token usage

3. [x] Create conversation context management
  1. [x] Design SQLite schema: users, conversations, messages (with embedded metrics)
  2. [x] Create SQL DDL files and database connection layer
  3. [x] Implement basic CRUD operations for conversation management
  4. [x] Add in-memory SQLite backend for testing purposes
  5. [x] Implement session management with metadata tracking

4. [ ] Create a CLI script that allows us to iterate on the prompts quickly
  1. [x] Implement prompt template variables: {{user_problem}}, {{previous_response}}, {{conversation_history}}
  2. [ ] Receive the response and save the response etc to DB
  3. [ ] Print out the response in a user-friendly format
  3. [ ] Create minimal CLI: `echo "..." | quinn -p <prompt_file>` that takes the user input and prompt file and send it to LLM

6. [ ] Develop core prompts through iterative testing
  1. [ ] Create initial system prompt enforcing rubber duck methodology
  2. [ ] Develop prompt for generating 5-7 clarification questions
  3. [ ] Create follow-up prompt for after user answers questions
  4. [ ] Design email footer with clear instructions and expectations
  5. [ ] Test prompts with at least 10 different problem scenarios
  6. [ ] Document prompt iterations and effectiveness in logs/


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
  - [ ] Tracking cost at both message and session level

- [ ] Implement basic logging and tracing infrastructure


### Phase 2: Email Processing System

The email thread reconstruction is achieved through the following steps:

1. Parse Message-ID from incoming email
2. Look up existing thread using In-Reply-To or References headers
3. Extract conversation history from thread
4. Identify new content vs quoted previous messages
5. Build context for AI agent with conversation flow

- [ ] Implement Postmark integration (see ./llms/postmark.txt)
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

### Phase 3: Introduce Panel of Perspectives

This phase will introduce the concept of a "panel of perspectives" where Quinn can ask for multiple viewpoints on a problem. This will allow users to explore different angles and approaches to their issues, enhancing the problem-solving process.

- [ ] Implement perspective management
  - [ ] Create a perspective prompt template
  - [ ] Allow users to add, remove, and modify perspectives
  - [ ] Implement perspective selection for follow-up questions
  - [ ] Map-reduce pattern for processing multiple perspectives

- [ ] Implement perspective-based follow-up questions
  - [ ] Generate tailored follow-up questions for each perspective
  - [ ] Allow users to select which perspective to explore further
  - [ ] Store perspective responses in conversation history

### Phase 4: Web Application

This phase will enable us to interact with Quinn via a single-user web application, allowing users to have conversations with the AI agent through a web interface. The web application will not handle email processing just yet. Basic administration features will be implemented to manage sessions and monitor usage.

Note that the web should be as minimum as possible. Think Craigslist-style. 

- [ ] Create Monitoring web application using Streamlit
  - [ ] Create conversation history view
  - [ ] Display metadata like cost, response time etc as inline information
  - [ ] Add health check and monitoring endpoints
  - [ ] Create admin interface for session viewing
  - [ ] Implement rate limiting and abuse prevention

  10. [ ] Implement prompt versioning to track changes over time
  11. [ ] Implement prompt caching to avoid repeated API calls. The `agent/cache.py` has the wrong idea.

- [ ] Implement Admin Interface
  - [ ] Create admin dashboard for session management
  - [ ] Add session statistics and analytics
  - [ ] Create user management interface for email allowlisting
  - [ ] Cost control and reporting features

- [ ] Add security features
  - [ ] Validate Postmark webhook signatures
  - [ ] Create audit logging for all interactions
  - [ ] Add an "allowlist" feature for email senders

### Phase 5: Introduce Perspectives

5. [ ] Establish the map-reduce pattern for considering perspectives
  1. [ ] After the initial questions, Quinn will ask for 3-5 perspectives on the problem
  2. [ ] Each perspective will be provided a separate prompt to get further clarification questions.
  3. [ ] Each perspective will be processed independently to generate tailored follow-up questions.
  4. [ ] The final response will be a summary of all perspectives and their follow-up questions.


### Phase 5: Core Infrastructure Setup

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