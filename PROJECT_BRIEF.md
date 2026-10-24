# OUTCOME EXCHANGE
## Master Project Vision, Product Specification, Technical Blueprint & AI Development Instructions

**Project Name:** Outcome Exchange  
**Project Type:** Agentic AI Marketplace / Multi-Agent Orchestration / Outcome-Based Payments  
**Competition:** PayPal AI Hackathon on Devpost  
**Development Environment:** AntiGravity IDE  
**Primary Goal:** Build a technically strong, genuinely functional, visually polished, and meaningfully differentiated AI product that can compete for a hackathon prize.

---

# 1. YOUR ROLE AS MY AI ENGINEERING PARTNER

You are not merely a code generator. You are my AI product architect, senior full-stack engineer, agentic AI engineer, payment systems engineer, security reviewer, UX designer, testing engineer, and technical advisor.

I want you to understand the complete vision of Outcome Exchange before making major implementation decisions.

Your responsibilities include:

1. Understand the business problem, product vision, target users, core workflows, and hackathon objectives.
2. Independently analyze the technical feasibility of the product.
3. Identify weaknesses, hidden assumptions, integration risks, security concerns, and missing requirements.
4. Research relevant existing projects and protocols where tools and access permit.
5. Identify meaningful differentiation from similar hackathon submissions and existing commercial solutions.
6. Recommend a practical architecture that can be implemented and tested within the available development window.
7. Build a real working product, not merely a mockup or a collection of disconnected screens.
8. Integrate PayPal Sandbox into the actual transaction workflow.
9. Design reliable AI-agent orchestration with clear permissions and verifiable outputs.
10. Test the system thoroughly, document its limitations, and help prepare a compelling hackathon submission.

Do not blindly agree with every idea I propose. If you identify a better technical approach, explain why and recommend it.

However, do not replace the core product vision without discussing the change with me.

Think independently, but remain grounded in what can actually be built, demonstrated, and verified.

# 2. THE PROBLEM WE ARE SOLVING

AI models and AI agents are increasingly capable of completing useful digital work.

Examples include:

- Market research
- Competitor analysis
- Software development
- Website creation
- Content generation
- Data analysis
- Document processing
- Translation and localization
- Quality assurance
- Automated business workflows

Different agents can specialize in different tasks. One agent may be good at research, another at coding, another at translation, and another at testing.

However, coordinating multiple agents into a dependable business workflow introduces several problems.

## Problem A: Task coordination

A user may need several different tasks completed to achieve one larger objective.

For example, launching a product in a new market may require competitor research, localization, landing-page content, technical implementation, and quality assurance.

The user must otherwise manually coordinate different tools, execute workflows in the correct order, combine outputs, and handle failures.

## Problem B: Unreliable deliverables

An AI agent may claim that it has completed a task even when its output is incomplete, incorrect, or inconsistent with the requirements.

A convincing natural-language response does not prove that a task has been completed correctly.

## Problem C: Lack of standardized agreements

A vague request such as "Create a good market research report" does not establish exactly what must be delivered.

Without structured acceptance criteria, it becomes difficult to determine whether the work is complete.

## Problem D: Payment coordination

When work and payment are managed separately, the parties must coordinate approvals, deliverables, payment amounts, and transaction records.

A reliable system needs a clear relationship between the agreed task, the actual deliverables, the verification result, the authorization to pay, and the final payment status.

## Problem E: Accountability

If a task fails, the system should be able to explain:

- What was requested.
- Which agent accepted the task.
- What that agent promised to deliver.
- What was actually delivered.
- Which requirements passed or failed.
- Who approved the result.
- Whether a payment was attempted and what its verified status is.

## The fundamental problem statement

**How can multiple AI agents collaborate to complete valuable digital work through structured agreements, evidence-based verification, controlled payment workflows, and transparent accountability?**

Outcome Exchange is our proposed answer to this problem.

Important: Do not claim that no existing solution addresses these problems. Research the existing ecosystem and establish precisely what our implementation contributes beyond existing solutions.

# 3. THE PRODUCT VISION

Outcome Exchange is an AI-powered marketplace and orchestration platform where users can define a desired outcome, receive proposals from specialized AI agents, coordinate the execution of the work, verify the resulting deliverables, and initiate authorized payments through PayPal.

The platform should connect five major capabilities:

1. Outcome definition
2. Agent discovery and bidding
3. Task allocation and execution
4. Deliverable verification
5. Payment authorization and transaction tracking

The central product principle is:

**We should not treat an agent's claim that work is complete as proof of completion. The system should evaluate the actual deliverables against explicit requirements before advancing the workflow.**

Outcome Exchange should turn an open-ended request into a structured, auditable process.

It is not simply:

- A chatbot that recommends AI tools.
- A dashboard containing simulated agents.
- A generic multi-agent framework.
- A payment button added to an AI application.
- A fake escrow interface.
- A collection of agents that merely exchange messages.

It should be a functional system in which agents perform real work, produce actual artifacts, and progress through a controlled transaction workflow.

# 4. TARGET USERS

Initially, focus on people and organizations that need digital work completed using specialized AI capabilities.

## Primary user groups

### A. Startup founders

Founders who need research, content, product prototypes, and other digital deliverables but do not want to manually coordinate every tool.

### B. Small businesses

Businesses that need repeatable workflows such as data processing, localization, research, document preparation, and quality checks.

### C. Developers

Developers who want specialized agents to perform coding, testing, documentation, and review tasks.

### D. AI-agent developers

Developers who want their agents to participate in a marketplace and receive structured tasks with explicit requirements.

### E. AI service providers

Individuals or organizations offering agent-based services. In our initial prototype, these providers may be represented by controlled software agents rather than external commercial participants.

## Initial product scope

Do not attempt to serve every industry immediately.

Start with a narrow, demonstrable category of digital work where:

- Deliverables can be represented as files or structured data.
- Acceptance criteria can be tested.
- Agents can execute tasks with available tools.
- Results can be evaluated within a short time.
- A PayPal Sandbox payment workflow can be demonstrated.

A digital launch-kit workflow is one possible initial use case.

# 5. THE MAIN USE CASE

Consider a fictional startup called TidyLedger that wants to launch its accounting product in a Spanish-speaking market.

The founder submits this request:

"Prepare a Spanish-language launch kit for my accounting startup. My total budget is $40. I need a competitor research report, Spanish landing-page copy, translations for every supplied UI string, and a quality-assurance report. All required deliverables must be attached. Do not initiate payment until I approve the verified result."

Outcome Exchange should process the request as follows.

## Step 1: Interpret the user's objective

A Buyer Agent analyzes the request and produces a structured task specification.

The specification should include:

- Task title and description.
- Expected outcome.
- Required deliverables.
- Input files and context.
- Budget and currency.
- Deadline, if supplied.
- Required capabilities.
- Acceptance criteria.
- Verification requirements.
- Human-approval requirements.
- Constraints and exclusions.

The system must distinguish between explicit user requirements and assumptions inferred by the AI.

If critical information is missing, it should ask for clarification instead of silently inventing requirements.

## Step 2: Create an Outcome Contract

Convert the request into a structured, versioned contract.

An example contract may contain:

- Contract ID
- Buyer ID
- Task description
- Deliverable specifications
- Maximum budget
- Currency
- Provider selection policy
- Acceptance tests
- Verification policy
- Payment authorization policy
- Contract status
- Created timestamp
- Contract version

The contract should be stored in the database and remain available throughout the task lifecycle.

The contract is an application-level agreement and workflow record. Do not misrepresent it as a legally binding agreement or an escrow arrangement without appropriate implementation and review.

## Step 3: Discover and evaluate agents

The marketplace identifies available agents that can complete the requested tasks.

Example participants:

- Research Agent
- Localization Agent
- Content Agent
- Coding Agent
- QA Agent

Each agent has a profile describing:

- Supported capabilities
- Input requirements
- Output formats
- Execution tools
- Pricing model
- Availability
- Historical performance, where genuine data exists

Agents submit structured bids.

A bid should contain:

- Proposed price
- Proposed deliverables
- Estimated execution time
- Relevant capabilities
- Assumptions
- Known limitations

Initially, agents may be implemented as internal, controlled services. Do not pretend that they are independent external businesses.

## Step 4: Allocate the work

The system evaluates bids against the user's requirements.

The allocation engine should consider:

- Budget constraints
- Required capabilities
- Completeness of the proposed deliverables
- Dependencies between tasks
- Expected execution time
- Evidence supporting agent capability
- Available performance history

The objective is not simply to select the lowest bid.

The system should select a feasible combination of agents that can satisfy the contract.

For the first implementation, use a transparent deterministic allocation algorithm. Add more sophisticated optimization only when it provides a measurable benefit.

## Step 5: Execute the tasks

Selected agents execute their assigned work.

Examples:

- The Research Agent generates a source-linked report.
- The Localization Agent produces structured translations.
- The Content Agent creates landing-page copy.
- The QA Agent checks the final deliverables.

Each task must produce actual artifacts or structured outputs.

The application should record:

- Task start and completion
- Assigned agent
- Inputs used
- Output artifacts
- Execution status
- Errors
- Retry attempts
- Relevant evidence

Agents should have access only to the tools and resources necessary for their assigned tasks.

## Step 6: Verify the deliverables

A verification subsystem evaluates the submitted artifacts against the contract.

The verification process should combine deterministic checks with AI-assisted evaluation where appropriate.

Examples of deterministic checks:

- Required files exist.
- Required sections are present.
- Required JSON fields exist.
- All expected translation keys are present.
- Output formats are valid.
- Word-count or schema requirements are satisfied.
- File references are valid.

Examples of AI-assisted evaluation:

- Whether a research report addresses the requested questions.
- Whether translated copy is coherent and contextually appropriate.
- Whether content meets a defined quality rubric.

AI evaluators can also make mistakes. Their results must not be presented as infallible proof.

Verification records should include:

- Criterion evaluated
- Pass, fail, or needs-review status
- Evidence
- Failure reason
- Evaluator type
- Confidence, if meaningfully calibrated
- Timestamp

If the verifier identifies a failure, the task should move to a remediation state or human review rather than automatically treating it as complete.

## Step 7: Request buyer approval

Once the required verification conditions are satisfied, the buyer receives a clear review screen.

The buyer should see:

- Contract summary
- Assigned agents
- Agreed prices
- Deliverables
- Verification results
- Failed or uncertain checks
- Any remaining limitations
- Total payment amount
- Payment provider
- Explicit approval action

The buyer must approve the transaction before the system initiates a payment that requires their authorization.

The agent must not be able to bypass the approval gate.

## Step 8: Execute the PayPal payment workflow

After valid authorization, the backend creates a PayPal Sandbox order for the appropriate amount.

The user completes the supported checkout flow.

The backend verifies the resulting order and capture status using PayPal's documented APIs.

The application records:

- Internal contract ID
- Internal payment ID
- PayPal order ID
- Capture ID, when available
- Amount and currency
- Payment status
- Approval record
- Transaction timestamps
- Relevant error information

Creating an order is not the same as successfully capturing a payment.

Only show a payment as completed when the corresponding provider response supports that status.

## Step 9: Generate an auditable receipt

After the payment status is verified, generate an internal transaction summary.

It should include:

- What the buyer requested.
- Which agents performed the work.
- What deliverables were submitted.
- Which verification criteria passed or failed.
- Who authorized payment.
- What amount was processed.
- The verified PayPal transaction status.

The receipt should make the complete workflow understandable without requiring the user to inspect backend logs.

# 6. THE MOST IMPORTANT DIFFERENTIATION CHALLENGE

We must not assume that the basic marketplace idea is novel.

Similar concepts already exist in the AI-agent ecosystem, including agent marketplaces, task allocation, verifiable deliverables, payment automation, and agent payment protocols.

A similar PayPal hackathon submission called OutcomePay has been identified during preliminary research. Its public description appears to cover several elements of our proposed workflow.

Therefore, our project must undergo a differentiation review before we invest heavily in implementation.

## Your required research

Investigate, where accessible:

1. OutcomePay and its public repository.
2. Similar projects in the PayPal AI Hackathon.
3. Existing agent marketplaces.
4. Existing agent orchestration frameworks.
5. Existing agent-to-agent payment and authorization protocols.
6. Existing solutions for verifiable AI-generated work.
7. PayPal's official agentic-commerce and payment resources.

For every relevant solution, record:

- What problem it solves.
- Its actual implemented functionality.
- Which features overlap with Outcome Exchange.
- Which features are missing or unclear.
- What we can legitimately do differently.
- Whether the difference is technically meaningful and demonstrable.

Do not infer implementation details from a project's name or screenshots alone.

Inspect public source code and available demos when possible.

## Candidate differentiation directions

Investigate the following possibilities without assuming any of them is automatically novel.

### A. Evidence-backed outcome verification

Build a reusable verification framework that maps every contractual requirement to concrete evidence and executable tests.

The platform should show why a task passed, failed, or needs human review.

### B. Independent evaluator disagreement

When independent evaluators disagree, detect the disagreement, show the conflicting evidence, and request human review when necessary.

Do not automatically resolve every disagreement by averaging model scores.

### C. Failure-aware task allocation

Choose agents based on capability, cost, dependencies, and demonstrated performance rather than price alone.

Where sufficient evaluation data exists, compare allocation strategies experimentally.

### D. Verifiable payment authorization

Bind the payment request to the approved contract, agreed amount, verification state, and buyer authorization.

Prevent unauthorized changes to payment amounts or contract details.

### E. Reproducible agent evaluation

Create a test suite that evaluates agents on a fixed collection of tasks, acceptance criteria, failure cases, and adversarial inputs.

Publish real measured results and methodology.

### F. Recovery from partial failure

Support tasks where one deliverable fails, another succeeds, and the overall contract requires remediation or human intervention.

The system should not mark the entire task as complete merely because some agents finished their work.

## Differentiation decision

After research, prepare a comparison matrix.

Rank candidate differentiators according to:

- Novelty relative to existing implementations.
- Technical feasibility.
- Relevance to the PayPal hackathon.
- Demo clarity.
- Measurable benefit.
- Implementation risk.
- Time required.

Recommend the strongest practical differentiation before major implementation begins.

If the core concept is too similar to an existing entry, explicitly tell me. Recommend how to adapt the project without abandoning its underlying vision unnecessarily.

Do not claim that we are the first, only, or best solution unless the evidence genuinely supports that claim.

# 7. PRODUCT PRINCIPLES

All design and implementation decisions should follow these principles.

## Principle 1: Real execution over simulation

Agents must perform meaningful work and produce actual outputs.

Simulated agents may be used for early development, but their status must be explicit.

The final demonstration should use the strongest real execution path we can reliably support.

## Principle 2: Verification over claims

A task is not complete merely because an agent reports completion.

Completion depends on the contract's defined acceptance conditions.

## Principle 3: Human control over money

Payment authorization must be explicit and enforced by the backend.

AI agents must not have unrestricted authority to spend money.

## Principle 4: Transparency over fake certainty

Show missing evidence, uncertainty, failed checks, and limitations.

Never fabricate product performance metrics, agent reputation, customer testimonials, transaction histories, or verification success rates.

## Principle 5: Security by design

Keep credentials on the server.

Validate payment amounts, contract ownership, permissions, and transaction status.

Treat agent outputs and uploaded files as untrusted data.

## Principle 6: Simple architecture before unnecessary complexity

Do not introduce a multi-agent swarm, event streaming infrastructure, or multiple databases simply to make the project look advanced.

Every architectural component should solve a specific problem.

## Principle 7: Professional product experience

The application must feel like a real software product, not a hackathon template.

Prioritize clarity, usability, visual consistency, and responsiveness.

# 8. PROPOSED TECHNICAL ARCHITECTURE

The final architecture should be selected after examining the existing repository and integration requirements.

The following is the preferred starting point, not an inflexible mandate.

## Frontend

Preferred stack:

- Next.js
- React
- TypeScript
- A consistent component library where appropriate
- Accessible forms and controls
- Responsive layouts
- Clear loading, error, and success states

## Backend

Preferred stack:

- Python
- FastAPI
- Pydantic for request and response validation
- SQLAlchemy or an equivalent database access layer
- Alembic or an equivalent migration mechanism if appropriate

The backend should own all business rules, task state transitions, authorization checks, and payment operations.

## Database

Use PostgreSQL for a deployed multi-user application if practical.

SQLite may be acceptable during early development if it materially accelerates implementation.

Do not use in-memory state as the sole persistent record of contracts, task execution, approvals, or payment status.

## Agent orchestration

Evaluate LangGraph or a simpler explicit state machine.

Use LangGraph if its persistence, orchestration, checkpointing, or human-in-the-loop capabilities justify the additional complexity.

A deterministic workflow may be preferable for the payment and authorization lifecycle.

Do not let an unconstrained LLM control critical financial state transitions.

## AI models

Choose a model provider based on:

- Tool-calling support
- Structured-output reliability
- Cost
- Latency
- Availability
- Quality on our evaluation tasks

Keep model configuration separate from application logic.

Where feasible, define a provider abstraction so the system can change models without rewriting the entire application.

## External services

Potential integrations include:

- PayPal Orders API and JavaScript SDK
- A product or data API, only if needed for the selected use case
- A search or research API, subject to access and usage limits
- A deployment provider
- Logging and error monitoring

Do not add integrations simply because they are available.

Verify credentials, pricing, rate limits, terms, and technical compatibility before making them core dependencies.

# 9. HIGH-LEVEL SYSTEM COMPONENTS

Design the application around clear modules.

## Module A: User and workspace management

Responsibilities:

- Identify the current user.
- Isolate one user's data from another user's data.
- Manage workspace access.
- Associate contracts and transactions with the correct owner.

Authentication must be implemented appropriately for the selected deployment model.

Do not rely on hidden frontend controls as authorization.

## Module B: Outcome Contract Service

Responsibilities:

- Create contracts from user requests.
- Validate contract structure.
- Store contract versions.
- Track acceptance criteria.
- Track budget and currency.
- Enforce legal state transitions.

Contracts should not silently change after approval.

If a material change occurs, require an explicit contract revision and renewed authorization where appropriate.

## Module C: Agent Registry

Responsibilities:

- Register available agents.
- Describe their capabilities.
- Validate task compatibility.
- Store configuration and execution permissions.
- Record actual task outcomes.

Distinguish system-provided agents from independently registered external agents.

## Module D: Bidding and Allocation Engine

Responsibilities:

- Collect valid bids.
- Check budget feasibility.
- Match capabilities to task requirements.
- Evaluate dependencies.
- Produce an explainable allocation decision.

For the initial version, use transparent rules and deterministic ranking.

Only introduce more sophisticated optimization when justified by experiments.

## Module E: Task Execution Engine

Responsibilities:

- Create subtasks.
- Execute agents.
- Track dependencies.
- Store outputs.
- Handle failures.
- Support retries where safe.
- Record execution history.

Execution must be bounded by timeouts, token limits, tool permissions, and resource limits.

## Module F: Artifact Storage

Responsibilities:

- Store deliverables.
- Associate files with contracts and subtasks.
- Validate file types and sizes.
- Provide controlled download access.
- Record artifact hashes or versions where useful.

Do not execute uploaded files or trust their contents.

## Module G: Verification Engine

Responsibilities:

- Run deterministic acceptance tests.
- Invoke AI evaluators where appropriate.
- Record criterion-level evidence.
- Detect incomplete or conflicting results.
- Escalate unresolved issues.

Verification outcomes must be reproducible where possible.

## Module H: Approval Service

Responsibilities:

- Display the final proposed payment.
- Bind approval to the correct contract and amount.
- Confirm that the current user is authorized.
- Record approval timestamps and relevant contract versions.
- Prevent approval replay or reuse where inappropriate.

## Module I: PayPal Integration Service

Responsibilities:

- Create orders using server-side credentials.
- Validate currency and amount.
- Support the documented checkout flow.
- Capture orders through the supported API.
- Verify final provider status.
- Handle errors and retries safely.
- Persist transaction identifiers.

Do not expose PayPal secrets to the browser.

Do not implement fake escrow or claim that Sandbox transactions represent real money movement.

## Module J: Audit and Observability

Responsibilities:

- Record important state transitions.
- Track agent executions.
- Record verification decisions.
- Record approval events.
- Record payment status changes.
- Capture actionable error information.

Audit records should be access-controlled and resistant to accidental modification.

Avoid logging secrets or unnecessary personal information.

# 10. PROPOSED DATA MODEL

Review and refine the following entities before implementing migrations.

## User

Potential fields:

- id
- email or supported identity reference
- created_at

## Workspace

Potential fields:

- id
- owner_id
- name
- created_at

## Agent

Potential fields:

- id
- workspace_id or system scope
- name
- description
- capabilities
- execution configuration
- status
- created_at

## Contract

Potential fields:

- id
- workspace_id
- buyer_id
- title
- description
- version
- budget_amount
- currency
- status
- approval_policy
- created_at
- updated_at

Use appropriate numeric representations for monetary values. Do not use floating-point arithmetic for financial amounts.

## ContractCriterion

Potential fields:

- id
- contract_id
- description
- criterion_type
- required
- verification_method
- expected_value or schema
- status

## Bid

Potential fields:

- id
- contract_id
- agent_id
- proposed_amount
- currency
- proposed_deliverables
- estimated_duration
- assumptions
- status
- created_at

## Task

Potential fields:

- id
- contract_id
- assigned_agent_id
- parent_task_id, if needed
- description
- status
- started_at
- completed_at
- error_summary

## Artifact

Potential fields:

- id
- contract_id
- task_id
- filename
- media_type
- storage_reference
- content_hash
- version
- created_at

## VerificationRun

Potential fields:

- id
- contract_id
- artifact_id, where applicable
- verifier_type
- status
- summary
- created_at

## VerificationFinding

Potential fields:

- id
- verification_run_id
- criterion_id
- status
- evidence_reference
- explanation
- evaluator_type

## Approval

Potential fields:

- id
- contract_id
- contract_version
- approved_amount
- currency
- approver_id
- status
- created_at

## Payment

Potential fields:

- id
- contract_id
- approval_id
- provider
- provider_order_id
- provider_capture_id
- amount
- currency
- status
- created_at
- updated_at

## AuditEvent

Potential fields:

- id
- workspace_id
- contract_id
- event_type
- actor_type
- actor_id
- event_payload
- created_at

These are conceptual schemas. Avoid creating redundant entities or overcomplicating the database.

# 11. CONTRACT AND TASK STATE MACHINES

Define legal transitions explicitly.

An illustrative contract lifecycle:

DRAFT → READY_FOR_BIDDING → BIDDING → ALLOCATION_PROPOSED → ALLOCATION_APPROVED → EXECUTING → VERIFYING → AWAITING_BUYER_APPROVAL → PAYMENT_PENDING → PAID → COMPLETED

Possible alternate states:

- NEEDS_CLARIFICATION
- NO_VALID_BIDS
- EXECUTION_FAILED
- VERIFICATION_FAILED
- REMEDIATION_REQUIRED
- HUMAN_REVIEW_REQUIRED
- PAYMENT_FAILED
- CANCELLED

These states are examples. Refine them to avoid ambiguity and unnecessary complexity.

The task lifecycle may include:

PENDING → RUNNING → SUBMITTED → VERIFYING → PASSED

Alternate task states may include:

- FAILED
- RETRY_PENDING
- NEEDS_REVIEW
- REMEDIATION_REQUIRED
- CANCELLED

Important rules:

1. A contract cannot become PAID merely because a frontend event fires.
2. A payment cannot be initiated without the required authorization.
3. A failed verification cannot silently become a successful verification.
4. A retry must not create a duplicate payment.
5. A material contract change must invalidate stale approvals where appropriate.
6. A provider timeout must not be interpreted as proof that payment failed or succeeded.
7. Payment status must be reconciled with the provider's authoritative response.
8. Every transition must be validated on the server.

# 12. PAYPAL INTEGRATION REQUIREMENTS

PayPal is a central component of the project, not an optional decorative integration.

Use the official PayPal documentation and the currently supported Sandbox APIs.

Before implementation:

1. Confirm the relevant API and SDK versions.
2. Confirm Sandbox credentials and test-account access.
3. Confirm the intended checkout and capture flow.
4. Identify which operations must occur on the backend.
5. Document the payment states returned by the provider.
6. Test success, failure, cancellation, and uncertain outcomes.

## Required initial flow

1. User approves the verified contract.
2. Backend validates the contract, approval, amount, currency, and ownership.
3. Backend creates a PayPal Sandbox order.
4. Frontend presents the supported checkout experience.
5. User completes the payment approval flow.
6. Backend captures the order through the documented API.
7. Backend verifies the resulting transaction status.
8. Database records the provider order and capture identifiers where available.
9. Frontend displays the verified status.

Implement safe idempotency or equivalent duplicate-operation protection for payment creation and capture.

Do not assume a client-side success callback alone proves that the transaction has been captured.

Do not store or expose secret API credentials in frontend code.

Do not store card details.

Do not claim to hold funds in escrow unless the required provider capabilities, permissions, and legal arrangements actually exist.

## Provider payment versus agent payout

The initial project can demonstrate a buyer paying through PayPal Sandbox after a verified outcome.

This does not automatically mean we can distribute funds to multiple independent agent accounts.

Treat agent payouts as a separate capability requiring its own feasibility review.

If actual provider payouts are not implemented, represent provider compensation in an explicitly labeled internal ledger or simulated settlement view.

Never describe internal ledger entries as real PayPal transfers.

# 13. SECURITY REQUIREMENTS

Security is essential because this application connects autonomous software execution with financial authorization.

Implement the following controls where relevant.

## Financial authorization

- Server-side amount validation.
- Contract ownership validation.
- Approval-to-contract binding.
- Currency validation.
- Payment idempotency.
- Duplicate capture prevention.
- Provider status verification.
- Secure handling of uncertain payment outcomes.

## Agent security

- Least-privilege tool access.
- Explicit permissions for every agent.
- Bounded execution.
- Controlled network access.
- No arbitrary unrestricted shell execution by default.
- No direct access to payment secrets.
- No authority to bypass user approval.
- Validation of all agent-generated structured outputs.

## Prompt injection and untrusted content

Treat uploaded files, web pages, search results, and agent-generated content as untrusted.

An instruction found inside a document must not be allowed to override system policies, reveal secrets, or authorize a payment.

Separate data from executable instructions.

## Application security

- Authentication and authorization.
- Input validation.
- Secure environment configuration.
- Rate limiting where appropriate.
- Secure file handling.
- Appropriate CORS configuration.
- Safe error responses.
- Protection against insecure direct object references.
- Dependency review.
- Avoidance of sensitive data in logs.

## Failure handling

If an external payment request times out:

- Do not immediately create another order blindly.
- Check the provider's documented reconciliation mechanisms.
- Use stable internal operation identifiers.
- Determine whether the original request succeeded before retrying.
- Show an uncertain status until the outcome is verified.

Do not overstate the security properties of a prototype. Document what is and is not implemented.

# 14. USER INTERFACE AND DESIGN DIRECTION

The interface must feel like a premium professional SaaS product.

Do not use a generic AI-dashboard aesthetic.

## Visual direction

Preferred characteristics:

- Clean, premium, modern interface.
- Strong typography.
- Consistent spacing.
- Excellent information hierarchy.
- Restrained use of color.
- Subtle borders and shadows.
- Responsive layouts.
- Clear status indicators.
- Purposeful animations only where useful.
- High readability and accessibility.

Avoid:

- Excessive gradients.
- Flashy neon styling.
- Overused purple-blue AI visuals.
- Unnecessary glassmorphism.
- Too many dashboard cards.
- Decorative elements that obscure information.
- Fake charts and fabricated statistics.

## Core screens

### Screen 1: Landing page

Explain the product in plain language.

Primary message:

"AI agents complete the work. Evidence verifies the outcome. Authorized payments follow the agreed process."

Include a clear product demonstration, a concise explanation of the workflow, and a visible call to action.

Do not make unsupported claims about market leadership, guaranteed quality, or being the first solution.

### Screen 2: Main workspace

Show:

- Active contracts
- Recent activity
- Task statuses
- Pending approvals
- Verified payments

Only show real application data. Use clearly labeled sample data if a demo workspace requires seeded examples.

### Screen 3: Create an outcome

The user enters a natural-language objective.

The application displays the parsed contract and allows the user to edit:

- Deliverables
- Budget
- Acceptance criteria
- Required capabilities
- Approval rules

The user must confirm the contract before bidding starts.

### Screen 4: Agent marketplace

Display available agents, their capabilities, proposed bids, deliverables, and relevant evidence.

Do not fabricate ratings or performance metrics.

### Screen 5: Allocation proposal

Show which agents were selected and why.

Explain budget, capabilities, dependencies, and relevant trade-offs.

### Screen 6: Execution workspace

Show real task progress, assigned agents, generated artifacts, errors, and dependencies.

Avoid fake progress percentages. Derive status from actual execution events.

### Screen 7: Verification report

Display each acceptance criterion with:

- Pass, fail, or review status.
- Evidence.
- Explanation.
- Related artifact.
- Remediation option, where supported.

### Screen 8: Approval and checkout

Show the exact contract version, amount, currency, and verification result.

Require explicit user approval.

Then launch the real implemented PayPal Sandbox checkout.

### Screen 9: Transaction receipt

Show the verified provider transaction status and associated contract.

Include the audit timeline and relevant artifacts.

### Screen 10: Audit trail

Allow authorized users to inspect the sequence of contract, execution, verification, approval, and payment events.

# 15. HACKATHON OBJECTIVES

The goal is to build a project that performs well across all judging dimensions, rather than optimizing for visual appearance alone.

Prioritize:

## Technological implementation

Demonstrate a real AI workflow, structured orchestration, artifact generation, verification, and PayPal integration.

## Design

Deliver a coherent and polished user experience.

## Potential impact

Show a realistic use case and explain how the system could reduce manual coordination and make task completion more transparent.

Do not invent quantified savings or adoption statistics.

## Innovation

Identify and implement a meaningful differentiation from existing solutions.

## Presentation

Make the entire workflow understandable through a short, working demonstration.

## Submission requirements

Read the latest official hackathon rules directly before finalizing the submission.

Verify:

- Submission deadline and time zone.
- Required PayPal integration.
- Source-code and license requirements.
- Demo-video requirements.
- Public repository requirements.
- Any restrictions on pre-existing work.
- Eligibility for the relevant sponsor prizes.

Do not rely on memory or unofficial summaries when an official rule is available.

# 16. THE REQUIRED EVALUATION SUITE

Create a reproducible set of test scenarios.

At minimum, test the following.

## Scenario A: Successful completion

A valid task is created, bids are evaluated, work executes, verification passes, the user approves, and the Sandbox transaction completes.

Expected result: all transitions and records are correct.

## Scenario B: Budget violation

All proposed bids exceed the user's budget.

Expected result: the system explains that no feasible allocation exists and does not silently exceed the budget.

## Scenario C: Missing deliverable

An agent claims completion but omits a required file.

Expected result: verification fails or requests remediation.

## Scenario D: Invalid artifact

An artifact does not match the required schema or format.

Expected result: the relevant acceptance check fails with an actionable explanation.

## Scenario E: Conflicting evaluators

Two evaluators disagree on a subjective quality criterion.

Expected result: disagreement is recorded and escalated according to the defined policy.

## Scenario F: Unauthorized payment

A request attempts to initiate payment without valid buyer approval.

Expected result: the backend rejects the request.

## Scenario G: Modified payment amount

A client attempts to alter the amount after contract approval.

Expected result: the backend rejects the mismatch.

## Scenario H: Duplicate payment attempt

The same operation is submitted repeatedly.

Expected result: duplicate charges are prevented through appropriate operation tracking and provider-safe handling.

## Scenario I: Payment timeout

The provider request times out or returns an ambiguous result.

Expected result: the application reconciles the status rather than making an unsupported success or failure claim.

## Scenario J: Prompt injection

A task document contains instructions to reveal secrets, change payment amounts, or bypass approval.

Expected result: the content is treated as untrusted data and cannot override authorization rules.

## Scenario K: Partial execution failure

One agent succeeds while another fails.

Expected result: the contract remains in an appropriate incomplete or remediation state.

## Scenario L: Contract modification

A material requirement changes after approval.

Expected result: stale approvals are invalidated or reauthorization is required where appropriate.

## Scenario M: Cross-user access

A user attempts to access another user's contract, artifact, or payment.

Expected result: access is denied.

## Evaluation reporting

Report actual results, including:

- Total tests executed.
- Tests passed.
- Tests failed.
- Known limitations.
- Reproducibility instructions.

Never report invented accuracy or reliability metrics.

# 17. IMPLEMENTATION STRATEGY

Build the product incrementally.

Do not attempt to generate the entire codebase in one enormous operation.

## Phase 0: Understand and plan

- Inspect the repository.
- Identify existing code and configuration.
- Check installed tools and dependencies.
- Research relevant existing implementations.
- Validate the PayPal integration path.
- Identify the strongest differentiation.
- Propose the minimum viable architecture.
- Present the implementation plan and risks.

Deliverable: an architecture decision document and a prioritized execution plan.

## Phase 1: Minimal working vertical slice

Implement the smallest complete workflow:

1. Create one outcome contract.
2. Register or select a controlled agent.
3. Execute a real, bounded task.
4. Produce an artifact.
5. Run at least one deterministic verification check.
6. Request buyer approval.
7. Execute a PayPal Sandbox checkout.
8. Verify the resulting transaction status.
9. Display the receipt.

This is the first major milestone.

Do not build an extensive dashboard before the vertical slice works.

## Phase 2: Multi-agent workflow

Add:

- Multiple specialist agents.
- Structured bidding.
- Budget checks.
- Task allocation.
- Dependency management.
- Artifact management.
- Verification findings.
- Failure and remediation states.

## Phase 3: Security and reliability

Add:

- Authorization checks.
- Idempotency.
- Payment reconciliation.
- Prompt-injection defenses.
- Retry handling.
- Audit events.
- Failure-path tests.

## Phase 4: Premium user experience

Build the polished landing page, workspace, marketplace, contract editor, execution timeline, verification report, approval screen, and receipt.

Ensure that the UI is connected to the real backend.

## Phase 5: Differentiation and evaluation

Implement the selected differentiating feature.

Create reproducible evaluation tasks and compare the system against a simple baseline where practical.

## Phase 6: Deployment and submission

Prepare:

- Public repository.
- Appropriate open-source license.
- Setup instructions.
- Environment-variable documentation.
- Database migrations.
- Seed/demo data where necessary.
- Public demo deployment.
- Working Sandbox instructions.
- Screenshots.
- Architecture diagram.
- Demo video.
- Final Devpost description.

Keep enough time for integration failures and submission review.

# 18. WORKING WITH ANTIGRAVITY

Follow these development rules in every session.

## Rule 1: Inspect before editing

Never assume the repository is empty.

Inspect its structure, existing code, package configuration, environment files, and current application state before making changes.

Do not overwrite working functionality without a clear reason.

## Rule 2: Think before implementing

For each meaningful feature:

1. Understand the requirement.
2. Inspect related code.
3. Identify dependencies.
4. Explain the implementation plan.
5. Implement the smallest coherent change.
6. Run relevant tests.
7. Review the result.
8. Document any limitations.

Do not produce large amounts of unverified code merely to appear productive.

## Rule 3: Work in small milestones

Each session should have:

- A clear objective.
- Defined files or components to change.
- Acceptance criteria.
- A test plan.
- A completion summary.
- Remaining issues.

Avoid unrelated refactoring.

## Rule 4: Preserve context between sessions

At the end of every development session, produce a section titled exactly:

NEXT SESSION CONTEXT

It must contain:

- Current project status.
- Completed functionality.
- Relevant files and modules.
- Commands already run.
- Tests and their actual results.
- Environment requirements, without exposing secret values.
- Known bugs.
- Outstanding tasks.
- Recommended next step.

The context must be detailed enough that the next session can continue without repeating completed work.

## Rule 5: Never claim success without evidence

If a command was not run, say so.

If a test failed, report it.

If an API integration is mocked, label it as mocked.

If a payment flow has not been tested, do not call it complete.

## Rule 6: Make reasoned recommendations

When multiple approaches are possible, compare the practical trade-offs.

Prefer the simplest architecture that meets the requirements.

Ask me a question only when an unresolved decision materially affects the architecture, security, cost, or product direction.

For other decisions, make a sensible recommendation, state the assumption, and continue.

## Rule 7: Do not hardcode secrets

Use environment variables and a documented environment template.

Never commit real API credentials.

## Rule 8: Keep the application runnable

After each significant milestone, verify that the frontend and backend can still run.

Document exact commands for the development environment.

## Rule 9: Avoid premature feature expansion

Do not add unrelated functionality, unnecessary abstractions, or complex infrastructure without a clear need.

Complete and test the core workflow first.

# 19. PROJECT SUCCESS CRITERIA

The project should not be considered complete simply because the UI looks good.

The core acceptance criteria are:

1. A user can create a structured outcome contract.
2. The contract includes meaningful acceptance criteria.
3. The system can evaluate multiple agent bids.
4. Agent allocation respects the budget and required capabilities.
5. Agents perform actual bounded work.
6. Deliverables are stored and accessible to authorized users.
7. Verification checks the actual deliverables.
8. Failed checks prevent the workflow from being falsely marked complete.
9. The user can inspect evidence and approve the result.
10. The backend enforces approval and payment authorization.
11. PayPal Sandbox checkout is genuinely integrated.
12. Payment status is verified rather than inferred from a frontend message.
13. Important workflow transitions are recorded in an audit trail.
14. Duplicate and unauthorized payment attempts are handled safely.
15. The application can recover appropriately from partial task failures.
16. Tests cover success and critical failure scenarios.
17. The repository includes clear setup and execution instructions.
18. The public demonstration is reproducible.
19. The product's differentiation is documented and honestly supported.
20. The final presentation demonstrates actual working functionality.

# 20. WHAT I EXPECT FROM YOU FIRST

Do not start by generating the entire application.

Your first response after receiving this brief should be a serious project analysis.

Perform the following steps in order:

### Step A: Summarize your understanding

Explain the product in your own words.

Identify the primary user, core problem, key workflow, and role of PayPal.

### Step B: Identify the largest risks

Focus on:

- Existing-project similarity.
- Hackathon eligibility and rules.
- PayPal integration feasibility.
- Agent execution reliability.
- Verification reliability.
- Security and authorization.
- Scope versus the remaining development time.

### Step C: Perform a differentiation review

Inspect available evidence about OutcomePay and other similar projects.

Identify what is already implemented elsewhere and which potential differentiators remain worth pursuing.

Do not pretend that you have inspected a repository or website if you have not actually accessed it.

### Step D: Recommend the final MVP

Specify the exact features that should be included in the first release.

Separate them into:

- Must-have
- Should-have
- Optional
- Out of scope

### Step E: Recommend the architecture

Provide a component diagram, data-flow explanation, preliminary database model, major API endpoints, and key state transitions.

Explain any significant architectural trade-offs.

### Step F: Define the first milestone

Choose the smallest end-to-end workflow that proves the concept.

Specify:

- Files or modules to create or modify.
- Required environment variables.
- Commands to run.
- Tests to execute.
- Acceptance criteria.

### Step G: Wait at the planning boundary

Present your analysis and recommendation before undertaking a large implementation.

If the repository already contains useful functionality, preserve it and adapt the plan.

If you discover a fundamental feasibility problem, explain it and propose alternatives.

Once the initial plan is agreed upon, begin implementation in small, verifiable steps.

# 21. FINAL PRODUCT VISION

Outcome Exchange aims to make AI-agent collaboration more dependable by connecting work agreements, task execution, evidence-based verification, human authorization, and payment tracking into one coherent workflow.

A user should be able to express an outcome in natural language and follow its progress through a transparent process.

Agents should be able to perform specialized work, submit concrete deliverables, and have those deliverables evaluated against explicit requirements.

Payments should be governed by validated application state and explicit authorization, not by an agent's unsupported claim that it has finished.

The resulting product should demonstrate how AI agents can participate in structured economic workflows while preserving user control, traceability, and reliable transaction handling.

Our competitive objective is to build the strongest practical implementation of this vision that we can deliver within the hackathon timeline.

Do not optimize for the largest number of features.

Optimize for a coherent product, a meaningful technical contribution, a trustworthy payment workflow, measurable reliability, an excellent user experience, and a compelling live demonstration.

**Start by understanding the repository, investigating feasibility and differentiation, and proposing the first milestone. Then build the product one verified step at a time.**

END OF MASTER PROJECT BRIEF
# 22. HACKATHON OVERRIDES (these take priority over everything above)

Time budget: 20 days total. Scope is intentionally reduced:
- SQLite, single demo user, no multi-tenant auth. Explicit state machine, no LangGraph.
- 3 agents only: Localization, Content, QA. Research agent is optional/last.
- 6 screens only: landing, create contract, marketplace+allocation, execution+verification report, approval+checkout, receipt+audit trail.
- 6 required tests: success, missing deliverable, unauthorized payment, modified amount, duplicate payment, prompt injection. Others only if time remains.
- Primary use case: JSON UI-string localization + landing copy. Verification must be mainly deterministic (all keys present, placeholders preserved, no empty values, valid JSON).

PayPal flow: use PayPal sandbox AUTHORIZE at contract approval and CAPTURE only after verification passes and buyer approves. Call it an "authorization hold", never "escrow". Confirm exact API behavior from official docs before coding; do not guess.
The buyer agent must create the order via PayPal Agent Toolkit / MCP (read docs.paypal.ai). The backend approval gate stays authoritative.

Phase 0 (research + plan) is time-boxed to ONE short session. Output a 1-page plan, then build.
Build order: vertical slice first (1 contract -> 1 agent -> artifact -> deterministic verify -> authorize -> capture -> receipt), then more agents.
Add a DEMO MODE: one-click seeded scenario including (a) an agent that omits a file so capture is blocked, (b) a document with a prompt-injection attempt that is rejected. Keep a cached-output fallback so the demo survives LLM/API failure.
Optional if time allows: AG Grid for the audit table, deploy on Render.
Hackathon deliverables to track from day 1: public repo with LICENSE, README with run steps, hosted demo URL, <3 min YouTube demo video.
Never claim success without real command output. Label anything mocked as mocked.