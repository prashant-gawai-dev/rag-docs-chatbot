# GoldenPi Knowledge Base: Bonds, Payments, and Customer Support

**Document type:** High-level RAG knowledge document
**Domain:** Bond investments, payment troubleshooting, order management, reconciliation, and escalation
**Audience:** Customer support, technical support, operations, and AI knowledge assistants

## 1. Purpose and Scope

This document provides foundational knowledge for answering common GoldenPi customer-support queries related to bond investments and payments.

The knowledge base covers:
- Basic bond and fixed-income investment concepts.
- The relationship between investments, payments, and orders.
- UPI and net banking troubleshooting.
- Payment success with missing or unconfirmed orders.
- Payment reconciliation and transaction mismatches.
- Evidence collection and payment gateway escalation.
- Support response guidelines and frequently asked questions.

**Important:** This is a general knowledge document, not an authoritative statement of every GoldenPi policy. Minimum investment amounts, fees, refund timelines, settlement timelines, supported instruments, and other product-specific rules must be verified against current official documentation.

---

# Part A: Bonds and Investment Basics

## 2. What Is a Bond?

A bond is a debt instrument through which an investor lends money to an issuer. The issuer may be a company, financial institution, government, or another eligible entity.

In return, the bond generally specifies the interest payments, principal repayment terms, maturity date, and other contractual conditions.

A bond investment is different from purchasing equity shares. A bondholder is generally a creditor of the issuer rather than an owner of the issuer.

**Example:** An investor purchases a bond issued by a company. The company agrees to pay interest according to the bond terms and repay the principal at maturity, subject to its contractual obligations and ability to pay.

The actual return and risk depend on the individual bond's terms, issuer, price, and market conditions.

## 3. Important Bond Terminology

### 3.1 Issuer

The issuer is the organization that issues the bond and is responsible for meeting its payment obligations under the bond terms.

Examples include companies, financial institutions, and government entities.

### 3.2 Face Value

Face value, also called nominal value or principal value, is the amount specified on the bond.

It is commonly relevant to interest calculations and repayment terms. The price paid by an investor in the market may differ from the face value.

### 3.3 Coupon Rate

The coupon rate is the stated annual interest rate associated with a bond's face value.

**Example:** A bond with a face value of ₹1,000 and a coupon rate of 8% per year has a stated annual coupon amount of ₹80, assuming the coupon is calculated on face value for a full year.

Actual payment frequency and amounts depend on the bond's terms.

### 3.4 Maturity Date

The maturity date is the date on which the bond's principal is contractually due for repayment.

The issuer's ability to meet that obligation is not guaranteed. Credit events, defaults, restructuring, or other contractual conditions can affect repayment.

### 3.5 Yield

Yield represents the return associated with a bond relative to its price and cash flows.

Yield is not always equal to the coupon rate. If a bond is purchased at a discount or premium to face value, its yield can differ from its coupon rate.

Yield to maturity is an estimate of the annualized return under specified assumptions, including holding the bond to maturity and receiving the expected cash flows.

### 3.6 Credit Risk

Credit risk is the possibility that the issuer will fail to make interest or principal payments as required.

Investors should examine the issuer's financial position, credit rating where available, rating outlook, security, and other relevant disclosures.

A credit rating is an assessment of credit risk, not a guarantee of repayment.

### 3.7 Liquidity Risk

Liquidity risk is the possibility that an investor may not be able to sell a bond quickly at a reasonable price.

A bond may have limited buyers or low trading activity. An investor who needs to sell before maturity may receive less than the purchase price.

### 3.8 Secured and Unsecured Bonds

A secured bond is backed by specified collateral or security interests, subject to the legal and contractual terms.

An unsecured bond does not have the same type of specified collateral backing its repayment obligations.

Security does not eliminate credit risk. Recovery depends on the enforceability and value of the security, priority of claims, and other circumstances.

### 3.9 Fixed and Floating Interest Rates

A fixed-rate bond generally pays interest at a stated rate according to its terms.

A floating-rate bond has an interest rate that changes according to a defined benchmark, formula, or contractual mechanism.

Investors should review the applicable rate formula, reset frequency, and payment conditions.

## 4. Common Bond Investment Questions

**Q: Are bonds risk-free?**

A: No. Bonds can carry credit risk, interest-rate risk, liquidity risk, reinvestment risk, and other risks depending on their structure and issuer.

**Q: Is the coupon rate the same as the return?**

A: No. The coupon rate is based on the bond's stated terms. The investor's actual return also depends on purchase price, cash flows, holding period, repayment, and other factors.

**Q: Can a bond's market price change before maturity?**

A: Yes. Market prices can change because of interest rates, issuer credit quality, market liquidity, and other factors.

**Q: Does holding a bond until maturity guarantee repayment?**

A: No. Repayment remains subject to the issuer's ability and obligation to pay and the bond's contractual terms.

**Q: Can an investor sell a bond before maturity?**

A: That depends on the instrument's transferability, market access, trading availability, and applicable rules. A sale may not be possible immediately or at the desired price.

**Q: What should a customer check before investing in a bond?**

A: Review the issuer, coupon, maturity, price, yield assumptions, credit rating where applicable, security, liquidity, cash-flow schedule, and offer or disclosure documents. Investment decisions should reflect the investor's financial objectives and risk tolerance.

## 5. Bond Investment Order and Payment Relationship

An investment transaction may involve several distinct stages:

1. The customer selects an investment and initiates the order process.
2. The platform processes the order request.
3. The customer attempts payment using an available payment method.
4. The payment gateway and relevant banking systems process the transaction.
5. The platform receives or retrieves transaction status information.
6. The investment order is confirmed or updated according to the applicable workflow.

This is a conceptual workflow, not a guarantee of the exact GoldenPi processing sequence for every product.

**Important distinction:** Payment status and investment order status are separate concepts. A customer may report that money was debited while the order remains unconfirmed. This discrepancy requires investigation rather than an assumption that either system is correct.

---

# Part B: GoldenPi Payment Support

## 6. Payment Gateway and Payment Methods

Payment gateways facilitate the processing of online payments between a customer, the relevant payment method or bank, and the merchant platform.

GoldenPi payment-support discussions have included Cashfree, UPI, and net banking. Specific incidents have also referenced other providers or platforms, including Razorpay and PhonePe. The gateway responsible for a particular transaction must be established from the actual transaction and integration records.

Common payment methods include:

- **UPI:** Payments initiated through a supported UPI application and linked bank account.
- **Net banking:** Payments initiated through a bank's online banking interface.
- **Other methods:** Availability depends on the current platform configuration and applicable payment-provider support.

The payment method selected by a customer does not, by itself, establish which gateway or integration processed the transaction.

## 7. UPI Payment Troubleshooting

### 7.1 UPI Application Is Not Visible

**Problem:** A customer cannot see or select their preferred UPI application while attempting payment.

**Recommended checks:**

1. Confirm which UPI application the customer is using.
2. Ask the customer to install a supported UPI application.
3. Ensure the customer's bank account is added to that application.
4. Ask the customer to reopen GoldenPi and retry the payment.
5. If the application remains unavailable, collect the device platform, application details, and relevant error evidence for technical investigation.

Previously discussed supported applications include PhonePe, Google Pay, Amazon Pay, Paytm, BHIM UPI, and CRED. Current availability should be verified against the active integration configuration.

An application visibility issue can arise from application compatibility, device-specific behavior, integration configuration, or other technical conditions. The exact cause must be established from evidence.

### 7.2 UPI Payment Failed

**Problem:** The customer attempts a UPI payment but cannot complete it.

**Recommended checks:**

1. Collect the exact error message.
2. Confirm the selected UPI application and linked bank account.
3. Record the approximate transaction time and amount.
4. Ask whether the customer sees a failed, pending, or successful transaction in the UPI application.
5. Check available gateway transaction records and platform logs.
6. If unresolved, escalate the evidence to the responsible payment gateway or technical team.

Do not repeatedly ask the customer to retry without considering whether a previous attempt may have debited the account.

### 7.3 UPI Payment Declined Due to a Security Issue

**Example:** The customer receives the message, "This payment is declined due to a security issue."

A security-related decline does not independently establish whether the cause is the customer account, beneficiary, UPI application, bank, risk controls, or gateway.

Collect the exact error, transaction reference, time, amount, application, and relevant gateway status. Escalate to the responsible provider for clarification.

If the customer can pay other beneficiaries but cannot pay one specific beneficiary, preserve that distinction in the investigation. It may help narrow the scope, but it does not prove the root cause.

## 8. Net Banking Payment Troubleshooting

### 8.1 Net Banking Payment Failed

**Problem:** A customer is unable to complete an investment payment through net banking.

**Recommended checks:**

1. Obtain the exact error message or a screenshot.
2. Record the transaction date, time, amount, and relevant order or transaction reference.
3. Ask the customer to verify their banking username or login details with their bank if the error relates to authentication.
4. Determine whether the transaction failed, remains pending, or resulted in a debit.
5. Inspect available gateway responses, payment records, and relevant application logs.
6. Share the evidence with the responsible payment gateway or bank team.
7. Request a clear status, root cause, workaround if available, and estimated resolution time from the responsible team.

Never request a customer's banking password, UPI PIN, OTP, or other secret authentication credentials.

### 8.2 Multiple Customers Experiencing Net Banking Failures

**Problem:** Net banking failures increase across multiple customers or transactions.

**Recommended investigation:**

- Compare failure rates over time.
- Group failures by payment gateway, payment mode, bank, and error code.
- Check whether failures are concentrated in one bank or affect multiple banks.
- Compare affected transactions with successful transactions.
- Inspect gateway responses, application logs, and relevant network or integration errors.
- Escalate with examples and quantitative evidence.

A broad increase in failures may indicate a gateway, integration, or network issue rather than a problem isolated to one bank. This is a hypothesis to investigate, not a confirmed root cause.

## 9. Payment Successful but Investment Order Not Confirmed

**Problem:** A customer reports a successful payment or debit, but GoldenPi displays an error such as "Something went wrong" and the investment order is not confirmed.

This scenario has appeared in GoldenPi payment-support discussions, including a reported payment through Ujjivan Small Finance Bank.

**Do not assume:**
- The payment is verified as successful merely because the customer reports it.
- The investment order was successfully created.
- The order was never created solely because it is not visible in the customer's interface.
- The money will automatically be refunded.
- A specific gateway or bank is responsible without supporting evidence.

**Recommended investigation:**

1. Collect the investment Order ID, if one exists.
2. Collect the payment gateway transaction reference and bank transaction details, where available.
3. Record the amount, transaction date, and approximate time.
4. Verify the transaction status in the relevant gateway records.
5. Check whether a GoldenPi order exists and whether it is pending, failed, confirmed, or otherwise recorded.
6. Inspect the available payment callback or webhook records and application logs.
7. Compare gateway status, platform payment records, and order status.
8. Escalate to the responsible gateway or internal technical team with the evidence.
9. Communicate the verified status and next steps to the customer.

The absence of an Order ID does not prove that no payment was attempted. Search using available transaction identifiers and timestamps.

If the correct gateway cannot be identified, gather the transaction details and use internal transaction records to determine which provider should be contacted.

## 10. Payment Reconciliation

Payment reconciliation is the process of comparing transaction records across the relevant systems to establish whether a payment has been correctly recorded and matched to the corresponding order.

Depending on the transaction workflow, the investigation may compare:

- GoldenPi order records.
- GoldenPi payment records.
- Payment gateway transaction status.
- Bank debit or settlement information.
- Payment callback or webhook records.
- Refund records, where applicable.
- Final order or investment completion status.

### 10.1 Common Reconciliation Scenarios

**Scenario A: Customer debited, order missing**

Verify the payment reference and gateway status, then search for the corresponding order. Investigate whether the order was created, whether a payment callback was received, and whether the transaction can be matched to an existing record.

**Scenario B: Gateway reports success, platform reports failure**

Compare the gateway response with platform payment and order records. Investigate callback delivery, processing errors, and status synchronization.

**Scenario C: Payment pending**

Verify the current gateway status and whether the bank or provider has completed processing. Do not treat a pending transaction as a confirmed success or failure without evidence.

**Scenario D: Duplicate payment or repeated debit**

Check whether multiple gateway transaction references exist and whether they correspond to the same order. Verify the actual transaction and refund status before communicating a resolution.

**Scenario E: Refund expected but not confirmed**

Check whether a refund was initiated, the recorded refund status, and any available reference or provider update. Provide a timeline only when it is supported by the applicable policy or confirmed provider information.

Reconciliation is not merely checking whether money was debited. It is matching the payment, order, and relevant provider records to establish the actual transaction state.

## 11. Payment Escalation Guidelines

A useful escalation should contain enough evidence for the receiving team to investigate without repeatedly asking for basic information.

### Information to Collect

- Customer or account reference, following internal privacy rules.
- Investment Order ID, if available.
- Gateway transaction ID or bank reference, where available.
- Payment method and bank name.
- Amount and transaction date/time.
- Exact error message or screenshot.
- Customer-reported debit or payment status.
- Verified gateway status, if available.
- Current platform order status.
- Relevant logs or callback evidence, where available.
- Steps already attempted and the outcome.

Never include passwords, OTPs, UPI PINs, or other authentication secrets in an escalation.

### Escalation Expectations

Request the responsible team to clarify:

1. Current transaction status.
2. Whether the payment was received, failed, or remains pending.
3. Why the payment and order statuses differ, if a mismatch is confirmed.
4. The identified root cause or remaining investigation.
5. Any verified workaround.
6. Expected next update or resolution timeline, where available.

Do not promise resolution times or refunds without verified information.

## 12. Payment Support Response Principles

When responding to a customer or internal stakeholder:

- Clearly state what has been verified.
- Distinguish customer-reported details from system-confirmed status.
- Ask for only the information needed to investigate.
- Avoid assigning blame to a bank or gateway without evidence.
- Explain the next action in plain language.
- Keep the response concise and professional.
- Do not close a ticket solely because a customer has stopped responding.
- Close a ticket when the issue is confirmed resolved according to the applicable support process.
- If a customer completes the investment through another attempt, verify the successful order before treating the issue as resolved.

---

# Part C: Frequently Asked Questions

## 13. General Payment FAQs

**Q: What should we do if a customer says payment succeeded but the order is missing?**

A: Verify the transaction against gateway and platform records, search for the corresponding order, and inspect available callback or webhook records. Collect transaction details and escalate the mismatch if it remains unresolved.

**Q: Which gateway should we contact for a payment issue?**

A: Identify the gateway from the actual transaction records. Do not select a provider based only on the payment method or bank name.

**Q: What is the difference between a payment failure and an order failure?**

A: A payment failure concerns the payment transaction. An order failure concerns the investment order. They are separate states and must be investigated independently.

**Q: What is a webhook?**

A: A webhook is an event notification sent by one system to another when a defined event occurs. In payment workflows, webhook events can communicate transaction status updates. Missing, delayed, or unsuccessfully processed events may contribute to a mismatch between systems, but the actual cause must be verified.

**Q: What is the difference between payment status and settlement status?**

A: Payment status describes the state of a payment transaction. Settlement status describes the movement or settlement of funds between the relevant parties. The exact meanings and available states depend on the provider and integration.

**Q: What should support do if the customer cannot provide an Order ID?**

A: Request available transaction details and search the relevant records using the available identifiers and timestamps. An Order ID should not be assumed to exist in every failed order-creation scenario.

## 14. Knowledge Assistant Rules

The RAG assistant should follow these rules when answering GoldenPi support queries:

1. Use the retrieved documentation as evidence.
2. Identify the payment method, bank, reported status, error message, and order status when provided.
3. Do not convert a customer-reported status into a verified system status.
4. Do not claim to have checked logs, databases, gateway dashboards, or bank systems unless that information is explicitly available in the provided evidence.
5. If the documents do not establish the root cause, state that it is unknown.
6. Recommend only documented or generally appropriate investigation steps.
7. Distinguish general bond education from GoldenPi-specific investment terms and policies.
8. Cite the source document or relevant section whenever possible.
9. If retrieved passages conflict, identify the conflict instead of choosing an unsupported answer.
10. If the information is insufficient, ask for the missing evidence or say that the available documentation does not answer the question.

## 15. Company-Specific Information Requiring Verification

Before using this document as an authoritative GoldenPi knowledge source, verify the following against current internal documentation:

- Supported bond products and eligibility requirements.
- Minimum investment amount and applicable fees.
- Investment order lifecycle and confirmation conditions.
- Supported payment methods, banks, and UPI applications.
- Active payment gateway mappings and merchant configurations.
- Payment failure, pending transaction, and refund procedures.
- Settlement and refund timelines.
- Ticket severity definitions and escalation contacts.
- Official customer communication and ticket closure policies.

Until verified, the assistant must not invent these values or present assumptions as GoldenPi policy.

**End of knowledge document.**