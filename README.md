# Quinn - AI-Powered Email Rubber Duck

<p align="center">
  <img src="docs/quinn.png" alt="Quinn Logo" width="256" height="256">
</p>

Quinn is an AI agent that helps you solve problems through guided reflection and clarification questions. Like rubber duck debugging, but smarter and conversational.

## What is Quinn?

Quinn operates as an email-based AI assistant at `quinn@postmark.alexdong.com`. Rather than providing direct solutions, Quinn helps you think through problems by:

- Asking targeted clarification questions
- Facilitating solution discovery through structured writing exercises
- Acting as an intelligent sounding board for complex decisions

As the wisdom from rubberduckdebugging.com reminds us:

> If ducks are so smart, why don't we just let the ducks do all the work? It would be wonderful if this were true, but the fact is that most ducks prefer to take a mentoring role.

Quinn follows this philosophy - the solution must come from you. Quinn simply helps you find it.

## How It Works

1. **Email Your Problem**: Send an email to `quinn@postmark.alexdong.com` describing your challenge
2. **Answer Clarifying Questions**: Quinn responds with structured questions to understand your situation
3. **Discover Your Solution**: Through the exchange, you'll clarify your thinking and identify the best path forward

## Example Session

Here's a real example of Quinn helping someone navigate a business partnership decision:

**User's Initial Problem:**
- Potential partnership opportunity with domain expert "Jonno"
- Strong business case but concerns about partner's reliability
- Need help deciding whether to proceed

**Quinn's Approach:**
1. Asked 7 categories of clarifying questions about partnership expectations, risk tolerance, decision-making, etc.
2. Analyzed responses to identify core issue: execution risk concentrated in unreliable partner
3. Proposed concrete 90-day proof-of-commitment sprint with specific deliverables
4. Provided templates for partnership agreements and kill criteria
5. Helped draft professional exit communications to preserve relationships

The entire exchange helped the user move from uncertainty to a clear action plan with defined success metrics.

## Core Principles

- **User-Driven Solutions**: Quinn guides but never dictates - you own the solution
- **Structured Thinking**: Questions are organized to surface key issues systematically  
- **Actionable Outcomes**: Sessions result in concrete next steps, not just insights
- **Professional Communication**: All interactions maintain a consultative, business-appropriate tone

## What Makes Quinn Different

Unlike traditional chatbots or AI assistants:
- **No Direct Answers**: Quinn won't solve problems for you - it helps you solve them yourself
- **Email-Based**: Asynchronous communication allows for thoughtful responses
- **Structured Methodology**: Each session follows a proven consultative framework
- **Context Preservation**: Email threads naturally maintain conversation history

## Technical Architecture

- **Email Interface**: Postmark API for reliable email send/receive
- **AI Engine**: Pydantic-AI for structured agent interactions and response validation
- **Infrastructure**: Cloudflare for DNS and email routing
- **Response Generation**: LLM prompts carefully crafted to maintain Quinn's consultative persona

### Implementation Details

**Email Processing Flow:**
1. Incoming emails received via Postmark webhook
2. Email content parsed and thread context extracted
3. Pydantic-AI agent processes request with conversation history
4. Response generated following Quinn's consultative patterns
5. Email sent back through Postmark API

**Prompt Engineering:**
- System prompts enforce Quinn's mentoring approach
- Structured output schemas ensure consistent question formatting
- Context windows maintain session continuity
- Validation rules prevent direct solution generation

## Use Cases

Quinn excels at helping with:
- Business partnership decisions
- Technical architecture choices
- Project prioritization
- Career transitions
- Strategic planning
- Conflict resolution
- Risk assessment

## Getting Started

Simply send an email to `quinn@postmark.alexdong.com` with:
1. A clear description of your challenge
2. Any relevant context or constraints
3. What kind of help you're looking for

End your email with: "Start by asking some clarification questions" to begin the structured discovery process.

## Response Time

Quinn typically responds within minutes during business hours. Complex queries may take longer as Quinn analyzes your situation to provide the most helpful questions.

## Interaction Patterns

Quinn follows specific patterns to maximize effectiveness:

### Initial Contact
- User describes problem with context
- Request for clarification questions triggers structured discovery
- Quinn responds with categorized, numbered questions

### Follow-up Exchanges
- User answers provide deeper context
- Quinn synthesizes information into actionable frameworks
- Concrete deliverables and timelines proposed
- Templates and communication drafts provided when needed

### Session Closure
- Clear next steps identified
- Decision criteria established
- Follow-up actions documented
- Graceful exit strategies prepared

## Session Management

- **Thread-Based**: Each email thread is a separate session
- **Context Aware**: Quinn maintains conversation history within a thread
- **Stateless Between Threads**: New threads start fresh
- **No Long-Term Memory**: Privacy-first approach means no cross-session data retention

## Running Your Own Instance

You can deploy your own Quinn instance with custom configuration:

### Configuration via config.toml

Create a `config.toml` file in your project root:

```toml
[email]
# Postmark configuration
postmark_api_key = "your-postmark-api-key"
postmark_server_token = "your-server-token"
inbound_email = "quinn@yourdomain.com"
from_email = "Quinn <quinn@yourdomain.com>"
webhook_url = "https://your-app.com/webhook/postmark"

[llm]
# AI model configuration
provider = "anthropic"  # or "openai"
model = "claude-3-opus-20240229"
api_key = "your-api-key"
temperature = 0.7
max_tokens = 4000

[quinn]
# Quinn behavior customization
name = "Quinn"
tagline = "Your AI-powered rubber duck"
# Customize Quinn's personality and approach
style = "consultative"  # options: consultative, socratic, coaching
max_questions_per_response = 7
response_delay_seconds = 30  # Prevent instant responses for more thoughtful feel

[security]
# Optional security settings
allowed_domains = ["yourdomain.com", "trustedpartner.com"]
rate_limit_per_hour = 10
require_auth_phrase = false  # Set to true to require a phrase in first email

[storage]
# Session storage (optional)
backend = "sqlite"  # options: sqlite, redis, none
sqlite_path = "./quinn_sessions.db"
session_ttl_hours = 168  # 7 days
```

### Environment Variables

Alternatively, use environment variables (overrides config.toml):

```bash
export QUINN_POSTMARK_API_KEY="your-key"
export QUINN_LLM_PROVIDER="anthropic"
export QUINN_LLM_API_KEY="your-llm-key"
export QUINN_INBOUND_EMAIL="quinn@yourdomain.com"
```

### Deployment Options

1. **Docker**: 
   ```bash
   docker run -v ./config.toml:/app/config.toml quinn:latest
   ```

2. **Cloud Functions**: Deploy to AWS Lambda, Google Cloud Functions, or Azure Functions with webhook endpoint

3. **Self-Hosted**: Run on any server with Python 3.12+ and public webhook endpoint

### Customizing Quinn's Behavior

Beyond configuration, you can modify Quinn's core behavior by editing the system prompts:

```python
# prompts/quinn_system.py
QUINN_SYSTEM_PROMPT = """
You are Quinn, an AI mentor who helps through questions, not answers.
{custom_instructions}
Never provide direct solutions - always guide users to discover their own.
"""
```

## Privacy

All conversations are confidential. Quinn does not store or share your information beyond what's necessary to maintain conversation context within a session.

---

Quinn: Because sometimes the best consultant asks questions instead of giving answers.