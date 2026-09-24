# GoldenPI Payment Gateway Escalation — Knowledge Base

This document captures recurring issue patterns, error codes, and communication templates used in GoldenPI/Oxyzo payment gateway (PG) support work involving Cashfree and Razorpay. Structured for chunking into a RAG pipeline (pgvector).

---

## 1. Error Codes & Decline Reasons Reference

### 1.1 Bank-Side Decline (SBI Example)
- **Source**: Cashfree
- **Bank**: SBI
- **Code**: 3044
- **Meaning**: Transaction declined at the bank's end (not a platform or PG-side issue). Common causes: insufficient balance, transaction limits, risk/fraud flags, temporary hold on online debits.
- **Customer action required**: Contact bank customer care/home branch to ask why the specific transaction was declined; confirm daily/per-transaction UPI or debit limit is sufficient; retry after bank confirms resolution.

### 1.2 Gateway Technical Error
- **Error Code**: GATEWAY_ERROR
- **Error Source**: gateway
- **Error Reason**: gateway_technical_error
- **Error Description**: "Your payment didn't go through due to a temporary issue. Any debited amount will be refunded in 5-7 business days."
- **Symptom pattern**: Customer selects Net Banking, is immediately redirected to an error page ("Payment Failed, Try Again"), unable to complete payment.

### 1.3 Risk Threshold Exceeded (Issuing Bank)
- **Error Code**: TRANSACTION_DECLINED
- **Error Source**: issuing_bank
- **Error Reason**: risk_threshold_exceeded
- **Error Description**: "The transaction declined due to risk checks by user's bank. Request user to check with their bank."
- **Symptom pattern**: Failures occur across both Net Banking and UPI payment options for the same customer, often with multiple repeated attempts.

### 1.4 Refund Timeline (Standard)
- If amount was deducted from customer's bank account, it is credited back within **5-7 working days** per standard PG SLA.
- Escalation to PG is generally NOT required unless:
  1. The 5-7 day window has already passed and refund is still not received.
  2. There is urgency/sensitivity (e.g., client relationship strain) warranting faster resolution.
  3. Refund confirmation (UTR/refund ID) is needed to close the loop with the customer.

---

## 2. Recurring Issue Pattern: BSE MID vs NSE MID Bank List Mismatch (Razorpay)

**Background**: GoldenPI transactions were earlier processed through the **BSE MID** on Razorpay. Following a switch to the **NSE MID**, a discrepancy was found: banks supported under the BSE MID's bank list are not necessarily present in the NSE MID's supported bank list.

**Specific case observed**: North East Small Finance Bank is supported under BSE MID but **not present** in NSE MID's supported bank list (per PG-side list). Since the customer's transaction was attempted through the NSE MID, the order itself was not created.

**Cross-reference check**: Customer was able to make payments using the same bank account via Razorpay on a different platform (Stable Money), and that bank was listed as Razorpay-supported per an earlier shared list — indicating the gap is specific to GoldenPI's NSE MID configuration, not a universal Razorpay limitation.

**Escalation ask to Razorpay**:
1. Confirm root cause of the mismatch despite earlier request to replicate BSE bank list to NSE.
2. Cross-check updated bank lists from both Razorpay and Cashfree to identify other supported banks not yet activated on the platform.
3. Request re-check for both **UPI and Net Banking** payment modes.
4. Timeline for resolution / alignment of NSE list with BSE list.

**MID reference format used in escalations**:
- BSE MID: [MID value]
- NSE MID: [MID value]

---

## 3. Recurring Issue Pattern: Customer Detail Mismatch on Cashfree Gateway (Direct NSE Transfers)

Cases flagged by Cashfree where amounts were transferred directly to NSE, with issues in customer detail visibility/capture. Requires RCA (Root Cause Analysis) request to Cashfree.

### Sub-pattern A — Order ID Not Generated (UPI)
- UPI transaction with no Order ID generated.
- Same customer/amount has a parallel Net Banking transaction where an Order ID WAS generated, but that transaction was "User Dropped."
- Customer details not properly available on gateway for the UPI transaction — resolved manually by cross-referencing the UPI ID in transaction logs.

### Sub-pattern B — Payment Processed Without KYC Completion
- Customer completes payment despite KYC not being completed on the platform.
- Same gap: customer details not properly available for UPI transaction on gateway; identified via UPI ID in logs.

### Sub-pattern C — Order ID Generated but Incomplete Customer Info
- Order ID generated successfully, but gateway does not display proper/complete customer information against the transaction.

**Common root issue across all sub-patterns**: Cashfree gateway not displaying complete/proper customer information for transactions, particularly where payment is directly transferred to NSE. This has led to at least one **chargeback**.

**RCA request structure to Cashfree**:
1. Why customer details are not captured/displayed correctly on the gateway for these transactions (specifically direct-to-NSE transfers).
2. Whether this is a systemic gap beyond the flagged cases.
3. Steps to prevent recurrence, given chargeback impact.
4. Supporting data provided via attached Excel with Cashfree Payment ID + Customer ID pairs per case.

---

## 4. Standard Escalation Email Structure (Template Pattern)

Used consistently across Cashfree/Razorpay/PG escalations:

1. **Subject line**: Concise, includes issue type + reference (Order ID/Customer ID) where applicable.
2. **Customer/Client details block**: Customer ID, Name, Contact Number (when relevant).
3. **Issue description**: What the customer experienced, in plain terms (e.g., "payment debited but order not confirmed," "redirected to error page immediately").
4. **Error details block**: Error Code / Error Source / Error Reason / Error Description, quoted verbatim from PG response.
5. **Order ID(s) / Payment ID(s)**: Listed individually, with dates if multiple.
6. **Specific ask**: Numbered list — root cause, timeline, confirmation of refund/status, or re-check request.
7. **Priority framing**: Note business impact (repeated customer attempts, client relationship strain, chargeback risk) to justify urgency.
8. **Sign-off**: Regards, Prashant Gawai.

---

## 5. Customer-Facing Response Templates

### 5.1 Bank Decline — Ask Customer to Check with Bank
> Thank you for reaching out regarding your recent transaction. We checked with our payment partner and found that the transaction was declined by your bank with decline code [X]. This means the rejection happened at the bank's end. Could you please contact your bank's customer care to ask why this specific transaction was declined, confirm your transaction limits are sufficient, and retry once your bank confirms the issue is resolved.

### 5.2 Escalation In Progress + Refund Status Check
> We have escalated this issue to [PG], and they are currently looking into it on their end. In the meantime, could you please confirm whether the refund amount has been credited to the customer's account?

### 5.3 Internal Ask — Which PG to Follow Up With
> Please confirm the Order ID against which the amount was debited. This will help us determine which PG to follow up with. Additionally, if possible, please share the bank transaction details related to the debited amount.

---

## 6. Internal Coordination Notes

- **Ram Dixit** — PM at GoldenPi/Oxyzo, internal contact for payment support/PG escalation decisions.
- **Saravanan** — Prashant's manager; looped in for high-severity client relationship issues (e.g., RM communication breakdown, escalations needing management visibility).
- **Prateek / Dharshan** — Cashfree-side contacts for escalation follow-ups (SBI escalation thread, refund status checks).
- Escalations are typically run in parallel across **email + WhatsApp group threads** with the PG, and internal stakeholders are looped into the same thread rather than a separate one, to maintain a single source of truth.

---

## 7. Escalation Severity Triggers (When to Push Harder)

An issue warrants escalation beyond routine follow-up when:
- Refund/resolution SLA (5-7 working days) has lapsed without update.
- Client has stopped responding to RM outreach or reported dissatisfaction/unprofessional handling.
- Same customer/amount shows **repeated failures** across multiple payment modes (Net Banking + UPI) or multiple attempts.
- A **chargeback** has already resulted from the underlying gap.
- A **known configuration gap** (e.g., bank list mismatch between MIDs) is causing recurring, predictable failures rather than a one-off decline.
