# Outcome Exchange — Final Demo Video Script (2 min 40 sec)

> **Competition Track:** PayPal AI Hackathon 2026 (Devpost)  
> **Target Video Duration:** 2 minutes 40 seconds (leaving a 20-second safety margin below the 3-minute ceiling)  
> **Target Application URL:** `http://127.0.0.1:8000/`  
> **Visual Evidence Policy:** Live top-bar badges explicitly declare `PAYPAL: SANDBOX (MOCK/LIVE)` and `AI: DETERMINISTIC FALLBACK/LIVE`. If recording without active API keys in `.env`, the narrator explicitly acknowledges the labeled Mock Sandbox engine. No simulation is ever represented as a live banking transaction.

---

## 1. Scene-by-Scene Timeline & Narration

| Timestamp | Phase | On-Screen Actions & Evidence | Spoken Narration (Clear, Confident, Crisp) |
| :--- | :--- | :--- | :--- |
| **0:00 – 0:15** | **1. The Problem & The Product** | Screen opens at `http://127.0.0.1:8000/`. Mouse hovers over brand header and the three system status badges (`PAYPAL: SANDBOX`, `AI ENGINE`, `Financial Release Gate: Authoritative`). | *"Autonomous AI agents can write code, copy, and translations—but in autonomous commerce, agents must never be allowed to invoice and pay themselves. If an agent hallucinates, drops deliverables, or claims work is finished without proof, buyer funds are lost. **Outcome Exchange** introduces buyer-governed outcome procurement: AI agents produce the work, deterministic checks verify the deliverables, and the buyer retains explicit release control over PayPal authorization holds."* |
| **0:15 – 0:40** | **2. Outcome Request & Contract (Gate 1)** | In Section 1, paste the natural-language request: *"Prepare a Spanish launch kit for our accounting startup. Translate UI keys preserving {variable} placeholders, generate landing page copy, and review. Budget: $40 USD."* Click **Analyze & Formulate Proposal**. The structured proposal renders. Click **Buyer Sign-Off: Confirm Terms & Create Contract ($40.00)**. | *"The buyer describes their outcome in plain English. The Buyer Agent parses the request into a formal contract with explicit acceptance criteria. Notice Gate 1: the human buyer must review and confirm the contract terms before any financial rails are touched. When approved, the system creates an official PayPal Orders v2 order with `intent: AUTHORIZE`. $40.00 is placed on temporary hold on PayPal rails. Zero dollars leave the buyer's account—no escrow, but delayed capture."* |
| **0:40 – 1:10** | **3. Multi-Agent Fulfillment** | In Section 2, click **Create Order via PayPal Agent Toolkit** and **Confirm Authorization Hold**. In Section 3, click **Run Multi-Agent Team**. Watch agent badges flip to `✓ Generated`. Switch through tabs (`es_translations.json`, `landing_page_es.md`, `qa_report.json`). | *"With the authorization hold active, three specialist agents execute: Localization, Content, and QA. The Localization Agent translates software strings while strictly preserving curly-brace interpolation tokens like `{user}`. The Content Agent writes a four-section landing page. The QA Agent provides cross-artifact review, but notice: the QA agent is strictly advisory. It cannot alter verification checks or trigger payments."* |
| **1:10 – 1:40** | **4. Verification Failure Blocks Payment** | Click **Scenario B: Verification Failure & Safe Recovery**. Watch the defective bundle execute with a missing section. Click **Run Full Deterministic Bundle Verification**. Red failure badges appear (`MISSING_SECTION`). Point to the locked Gate 2 and the red banner: *`VERIFIED PROOF (HTTP 400 Bad Request): Capture blocked: deliverable verification has failed checks: ['landing_page_required_sections']`*. | *"Here is our core differentiator: independent, deterministic code verification. Not an LLM judging itself, but hard Python and JSON checks. In Scenario B, we simulate an incomplete deliverable where the Call to Action was omitted. Verification fails with two red flags. Watch what happens: the payment release gate is physically LOCKED on the server. Even if an attacker calls the capture API directly, the backend strictly rejects the request with HTTP 400 Bad Request."* |
| **1:40 – 2:05** | **5. Recovery & Successful Verification** | In the demo bar, watch the automated recovery kick in (or click **Recover & Re-Run Verification**). Corrected deliverables generate. Click **Run Full Deterministic Bundle Verification**. All 10 checks turn green (`10 MANDATORY PASSED`). | *"To recover, the buyer triggers agent remediation. The agents regenerate complete deliverables, re-evaluating all 10 checks—syntax, key parity, interpolation tokens, and structural sections. Every mandatory check passes 100%. The server transitions the contract to `AWAITING_BUYER_APPROVAL`, and the payment release gate unlocks safely."* |
| **2:05 – 2:25** | **6. Gate 2 Approval & PayPal Settlement** | Scroll to Section 5. Point to the unlocked gate. Check the box: *"I have personally inspected the verified deliverables..."*. Click **Approve Deliverables & Capture $40.00 USD**. Section 6 animates into view showing the settled receipt and audit timeline. | *"Notice: passing verification does NOT automatically debit the buyer. Gate 2 requires explicit human buyer sign-off. When the buyer checks the confirmation box and approves release, the backend issues a delayed capture to PayPal Payments v2 with `final_capture: true`. Deterministic `PayPal-Request-Id` headers prevent duplicate charges, and the contract settles."* |
| **2:25 – 2:40** | **7. Differentiator & Closing** | Highlight the official transaction receipt (showing approved amount, PayPal Order and Capture IDs, verification score: 10/10) and scroll down the chronological audit timeline. | *"Here is the final receipt, with transparent provider attribution and the full chronological audit trail tracking every transition from DRAFT to PAID. Outcome Exchange bridges autonomous AI generation and global PayPal rails with genuine buyer governance. Thank you."* |

---

## 2. On-Screen Visual Checklist for the Operator

Ensure the following visual cues are distinctly legible on screen during the recording:
1. **Top Status Bar (0:05):**
   - Clearly visible `PAYPAL: SANDBOX (MOCK)` (or `LIVE`) pill.
   - Clearly visible `AI: DETERMINISTIC FALLBACK` (or `GEMINI/OPENAI`) pill.
   - Green `Financial Release Gate: Authoritative` badge.
2. **Acceptance Criteria Rationale (0:25):**
   - Step 1 proposal card showing the four explicit criteria rationale points.
3. **Multi-Agent Deliverable Tabs (0:55):**
   - Click `es_translations.json` to show `{user}` and `{email}` placeholders preserved.
   - Click `landing_page_es.md` to show `# Product Title` and the 4 `##` headers.
   - Click `qa_report.json` to show the qualitative QA verdict.
4. **Failure State & Locked Gate (1:25):**
   - Step 4 checklist showing red `✕ FAILED` on `landing_page_required_sections`.
   - Step 5 banner showing `CAPTURE STRICTLY BLOCKED` and disabled capture button.
5. **Human Gate 2 Checkbox (2:10):**
   - Explicit mouse click checking the buyer approval checkbox to unlock the capture button.
6. **Settled Receipt & Timeline (2:30):**
   - The completed receipt table with Order ID, Capture ID, $40.00 USD settlement, and the append-only activity timeline.

---

## 3. Technical Credibility Q&A (Judge Alignment)

- **Q: Why PayPal Authorization Hold rather than Escrow?**  
  *A:* True escrow is a regulated financial service requiring specialized money transmitter licensing. PayPal Orders v2 `intent: "AUTHORIZE"` provides an official, zero-escrow financial hold: funds are authorized on PayPal rails, and if deliverables fail, the authorization voids at $0 charge to the buyer.
- **Q: What happens if an agent experiences a timeout or malformed response?**  
  *A:* The application falls back transparently to a local deterministic rule engine (`is_fallback: true`). All fallback events are visibly badged in the UI and recorded in the audit trail. No fallback output is ever disguised as a live external completion.
- **Q: How are race conditions and duplicate captures prevented?**  
  *A:* At the application level, an asynchronous mutex (`_capture_lock`) serializes capture and void requests. At the payment network level, deterministic `PayPal-Request-Id` headers (`capture_{contract_id}_{auth_id}`) prevent duplicate charges across retries.
