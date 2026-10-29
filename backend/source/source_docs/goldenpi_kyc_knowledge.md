# Golden PI – KYC Registration Guide

**Source**: goldenpi.com
**Document Type**: Step-by-step KYC Verification Guide
**Purpose**: Complete Know Your Customer (KYC) process required before investing in bonds and fixed-income products on Golden PI.

---

## 1. Introduction

Golden PI (goldenpi.com) is an online platform for investing in fixed-income products such as bonds and fixed deposits. Before a user can invest, they must complete a one-time KYC (Know Your Customer) verification.

**Important Note – IPO Shortcut**:
If a user only wants to invest in an IPO, full KYC is not required. Only a verified PAN is needed to start investing in an IPO on Golden PI.

---

## 2. Account Creation Process

### Step 1: Visit the Website
- Go to goldenpi.com
- Click the **Login / Sign Up** button in the top-right corner of the homepage.

### Step 2: Choose Sign-Up Method
Golden PI supports three sign-up methods:
1. Mobile number
2. Email address
3. Google account

**Recommended flow in this guide**: Sign up using mobile number → Enter mobile number → Click Continue → Verify with OTP.

### Step 3: Enter Personal Details
After mobile OTP verification, the user must provide:
- Full name (exactly as it appears on PAN card)
- Email address

An OTP is sent to the email for verification.

**Note**: If the user signs up with email first, the platform will ask them to verify their mobile number instead.

---

## 3. Starting the KYC Process

Once the account is created:
- Go to the **Profile** page
- Click on the **Complete KYC** prompt (mandatory before buying any bond or investment product)

---

## 4. PAN Verification (Step 5)

- Golden PI automatically fetches PAN details from the Income Tax Department (ITD) database.
- User must review the auto-fetched details carefully (they cannot be changed later).
- Three mandatory declarations are pre-checked:
  1. I am a resident of India
  2. I am not a Politically Exposed Person (PEP)
  3. SEBI has not taken any action against me
- Click **Verify & Continue**

---

## 5. Selfie Verification (Step 6)

User must complete selfie verification for identity confirmation. Two options are available:

1. **Via Web** – Using laptop webcam
2. **Via Phone Camera** – Scan QR code and continue on mobile browser (Recommended)

**Technology used**: Hyperverge API
**Recommendation**: Use phone camera for clearer photo and faster approval.

---

## 6. Bank Account Verification (Step 7)

Two methods are supported:

### Method 1: Penny Drop
- User enters Bank Name, Branch/IFSC, and Account Number
- Golden PI credits ₹1 to the account to verify details

### Method 2: Reverse Penny Drop (UPI)
- User sends ₹1 to Golden PI via UPI
- Amount is refunded within 48 hours

**Technology used**: Hyperverge SDK

---

## 7. Signature Capture (Step 8)

User can provide signature in two ways:
1. **Draw** signature directly on the screen
2. **Upload** a photo of the signature
   - Must be on plain white background
   - Blue or black ink only
   - Maximum file size: 5 MB

Processed through Hyperverge platform.

---

## 8. Personal Profile (Step 9)

User must fill regulatory information required by SEBI:
- Father’s name
- Marital status
- Employment type
- Annual salary range
- Investing experience

Click **Confirm & Continue** after filling all fields.

---

## 9. Application Form Generation & KRA Check (Step 10)

Golden PI checks the user’s PAN against the **KRA (KYC Registration Agency)** database.

### Case A: KRA Record is Validated
- Golden PI automatically downloads existing data from KRA
- Application form is auto-populated
- No DigiLocker required
- User only reviews details and clicks **Verify & Continue**
- UCC is generated **instantly** after form creation

### Case B: KRA Record is Non-Validated
- User is redirected to DigiLocker
- Must enter Aadhaar number + OTP + DigiLocker M-PIN
- Grant permission to share Aadhaar and PAN documents
- Documents are attached on pages 6 and 7 of the application form
- UCC is generated only after DigiLocker + e-sign is completed

---

## 10. E-Sign the Application (Step 11)

- E-signing is done through **e-mudra.com**
- User enters Aadhaar number
- Receives OTP
- Must accept consent declaration authorizing e-Mudra Limited to use Aadhaar and OTP for e-signing

---

## 11. Link Demat Account (Step 12)

- User must link an active Demat account
- Enter the 16-digit Demat ID
- Bonds will be credited to this Demat account

---

## 12. UCC (Unique Client Code) Generation (Step 13)

UCC is the unique identifier that registers the user with the exchanges (NSE UCC and GSPL UCC).

- **Validated KRA**: UCC generated instantly after application form creation
- **Non-validated KRA**: UCC generated only after DigiLocker verification + e-sign is completed

This is the final backend registration step before the account can be marked as fully verified.

---

## 13. KYC Verification & Completion (Step 14)

- After submission, the application goes into verification
- If KRA was **not validated**, verification can take up to **48 hours**
- Once KYC status shows as **Verified**, the account is fully activated for investing

---

## 14. Tracking KYC Status (Step 15)

Users and internal teams can track the entire process using **Dealdesk** (Golden PI’s internal tool).

Dealdesk shows:
- CRM details
- Customer personal details
- KYC claim details
- Customer KYC documents (Photo, Proof of Identity, Proof of Address)
- Bank details
- Demat details
- Signature and other details
- Customer KYC stages with timestamps and verification status
- Option to create NSE UCC and GSPL UCC directly from the dashboard

---

## Summary of Key Technologies Used

| Step                  | Technology / Partner     |
|-----------------------|--------------------------|
| Selfie Verification   | Hyperverge API           |
| Bank Verification     | Hyperverge SDK           |
| Signature             | Hyperverge               |
| E-Sign                | e-mudra.com              |
| PAN Fetch             | Income Tax Department    |
| Document Fetch        | DigiLocker (if needed)   |
| Tracking              | Dealdesk (internal)      |

---

## Final Outcome

Once KYC status is marked as **Verified**, the user can start investing in bonds and other fixed-income products on Golden PI.