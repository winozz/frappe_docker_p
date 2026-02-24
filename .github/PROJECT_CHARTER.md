# Cavite State University (CvSU) Accounting Information System (AIS)

**Status:** Approved for Development  
**Framework:** Frappe/ERPNext  
**Deployment:** Phased Implementation (4 Waves)

---

## 📋 Project Overview

The CvSU AIS is a comprehensive accounting system designed to manage:
- Student Collections & Cashiering
- Disbursements & Budget Control
- Financial Reporting & Compliance
- Integration with Student Enrollment System
- UACS (Unified Accounts Code Structure) Chart of Accounts

---

## 🎯 Implementation Phases

### Phase 1: Foundation & Master Data (Weeks 1-4)

**Focus:** Establishing rules and connectivity

**Activities:**
- Data Migration: Import and clean UACS Chart of Accounts
- Strict tagging of valid Fund Clusters for each account
- Integration Setup: Configure API connection with Student Enrollment System
- Access Control: Define Role Profiles (Encoder, Budget Officer, Accountant, Cashier)

**Deliverable:** Read-Only environment for Chart of Accounts verification and Student record search

**Exit Criteria:**
- ✅ UACS Tree verified 100% accurate against COA Manual
- ✅ "Fetch Assessment" function successfully retrieves test student data

---

### Phase 2: Collections & Cashiering (Weeks 5-8)

**Focus:** Income generation efficiency

**Activities:**
- Pilot Testing: Deploy 5 Cashier stations at Main Campus
- Hardware Config: Setup printers for Official Receipt (OR) forms
- Training: Cashier training on "Fetch → Verify → Print" workflow

**Deliverable:** Functional Cashiering Module issuing ORs and generating Report of Collections and Deposits (RCD)

**Exit Criteria:**
- ✅ 100 consecutive live transactions processed without calculation error
- ✅ RCD balances with physical cash counts for 5 consecutive days

---

### Phase 3: Disbursements & Budget (Weeks 9-12)

**Focus:** Controlled spending

**Activities:**
- Budget Loading: Upload approved University Budget (GAA & STF) into Registry
- Workflow Activation: Enable "Box A → Box B → Box C" digital approval chain
- Printer Alignment: Calibrate printers for Landbank/DBP continuous checks

**Deliverable:** System generation of valid Checks and Advice to Debit Account (ADA) files

**Exit Criteria:**
- ✅ Zero "Overdraft" errors (System blocks payment when budget is zero)
- ✅ Tax computations (EWT/VAT) match manual Excel for 50 sample vouchers

---

### Phase 4: Reporting & Hardening (Weeks 13+)

**Focus:** Compliance and Audit integrity

**Activities:**
- Parallel Run: Compare System-Generated vs legacy Excel reports
- Audit Simulation: Internal Audit stress-testing
- Financial Reports: Trial Balance, FAR 1

**Deliverable:** Official sign-off on System-Generated Financial Reports

**Exit Criteria:**
- ✅ Trial Balance variances resolved (0.00)
- ✅ Internal Audit certifies Audit Trail integrity

---

## 💰 Calculation Scenarios

### Scenario A: Disbursement with VAT & EWT (Goods)

**Context:** Purchase of Office Supplies from VAT-Registered Supplier

**Given:**
- Gross Amount: ₱112,000.00
- Supplier Type: VAT Registered (Goods)
- Tax Base: Gross is VAT Inclusive

**Calculation Logic:**
```python
net_of_vat = gross_amount / 1.12  # ₱112,000 / 1.12 = ₱100,000.00
vat_5_percent = net_of_vat * 0.05  # ₱100,000 × 0.05 = ₱5,000.00
ewt_1_percent = net_of_vat * 0.01  # ₱100,000 × 0.01 = ₱1,000.00
total_deductions = vat_5_percent + ewt_1_percent  # ₱6,000.00
net_payable = gross_amount - total_deductions  # ₱112,000 - ₱6,000 = ₱106,000.00
```

**Journal Entry:**
```
Debit:  Office Supplies Inventory  ₱112,000.00
Credit: Due to BIR - VAT          ₱5,000.00
Credit: Due to BIR - EWT          ₱1,000.00
Credit: Cash in Bank              ₱106,000.00
```

---

### Scenario B: Disbursement with VAT & EWT (Services)

**Context:** Payment for Security Services

**Given:**
- Gross Amount: ₱56,000.00
- Supplier Type: VAT Registered (Service)

**Calculation Logic:**
```python
net_of_vat = 56000 / 1.12  # ₱50,000.00
vat_5_percent = 50000 * 0.05  # ₱2,500.00
ewt_2_percent = 50000 * 0.02  # ₱1,000.00 (Services = 2%)
total_deductions = 2500 + 1000  # ₱3,500.00
net_payable = 56000 - 3500  # ₱52,500.00
```

---

### Scenario C: Student Collection (Fund Splitting)

**Context:** Student pays full assessment

**Given:**
- Total Cash Received: ₱5,000.00
- Assessment Details:
  - Tuition: ₱3,000
  - Lab Fee: ₱1,000
  - Student Council: ₱500
  - Red Cross: ₱500

**System Distribution:**
```python
fund_164_tuition = 3000
fund_164_lab = 1000
trust_fund_student_org = 500
trust_fund_ngo = 500

# Deposit Requirements
to_landbank_account_a = fund_164_tuition + fund_164_lab  # ₱4,000.00
to_landbank_account_b = trust_fund_student_org + trust_fund_ngo  # ₱1,000.00
```

**Result:**
- To Landbank Account A (Fund 164): ₱4,000.00
- To Landbank Account B (Trust): ₱1,000.00

---

### Scenario D: Budget Utilization (Blocking)

**Context:** Attempt to purchase equipment with insufficient funds

**Given:**
- Current Allotment: ₱1,000,000.00
- Existing Obligations: ₱950,000.00
- Remaining Balance: ₱50,000.00
- New Purchase Request: ₱60,000.00

**System Action:**
```python
def validate_budget(purchase_amount, available_balance):
    if purchase_amount > available_balance:
        frappe.throw(
            f"Insufficient Allotment. Available Balance: ₱{available_balance:,.2f}",
            exc=InsufficientBudgetError
        )
    return True

# Check: Is ₱60,000 ≤ ₱50,000? False
# Result: HARD STOP - User blocked from saving
```

**Error Message:** 
```
"Insufficient Allotment. Available Balance: ₱50,000.00"
```

---

## ⚠️ Expectations Management

### For Executive Management

| Expectation | Reality |
|------------|---------|
| The system will fix historical data issues | The system cannot clean dirty historical data. Unbalanced ledgers from the past will remain unbalanced. **System ensures integrity for future transactions only.** |
| Approvals will be faster | Approvals will be **stricter**. Executives must digitally sign and cannot "verbally approve" payments. |

### For End Users (Encoders/Cashiers)

| Expectation | Reality |
|------------|---------|
| The system is flexible like Excel | The system is **rigid**. Users must select from valid lists (Payees, Accounts) and cannot manually type entries. This prevents audit findings. |
| Mistakes can be easily edited | Posted vouchers are **locked**. Corrections require formal Reversing Journal Entry. This is audit compliance, not a system limitation. |

### For The Technical Team

| Expectation | Reality |
|------------|---------|
| Deployment is a one-time event | Deployment is the **start of ongoing maintenance**. Tax rates, UACS codes, and fees change annually and require dedicated administration. |

### For Auditors

| Expectation | Reality |
|------------|---------|
| Digital signatures replace wet signatures immediately | While the system supports digital logs, **physical paper with wet signatures will likely remain required** for COA submission until full paperless policy is legally adopted. |

---

## 🔧 Technical Requirements

### System Architecture
- **Framework:** Frappe Framework v15
- **Database:** MariaDB 11.8
- **Frontend:** Vue.js (Frappe Desk)
- **Integration:** REST API for Student Enrollment System
- **Deployment:** Docker containers

### Key DocTypes to Develop
1. **Chart of Accounts** (UACS-compliant)
2. **Fund Cluster** (Fund tagging system)
3. **Official Receipt** (OR generation)
4. **Collection Entry** (Cashiering)
5. **Report of Collections & Deposits** (RCD)
6. **Disbursement Voucher** (Box A/B/C workflow)
7. **Budget Registry** (GAA & STF tracking)
8. **Tax Computation** (VAT & EWT calculation)
9. **Check Printing** (Landbank/DBP format)
10. **Audit Trail** (Immutable transaction log)

### Integration Points
- **Student Enrollment System API**
  - Endpoint: `/api/student/assessment`
  - Method: GET
  - Returns: Student details, assessment breakdown, payment status

### Compliance Requirements
- UACS Chart of Accounts compliance
- COA (Commission on Audit) standards
- BIR (Bureau of Internal Revenue) tax tables
- Government Accounting Manual (GAM) adherence

---

## 📊 Success Metrics

1. **Phase 1:** 100% UACS accuracy
2. **Phase 2:** Zero calculation errors in 100 consecutive transactions
3. **Phase 3:** Zero overdraft errors + 100% tax accuracy
4. **Phase 4:** Trial Balance variance = 0.00

---

## 🚀 Development Priorities

### Priority 1 (Critical Path)
- UACS Chart of Accounts DocType
- Fund Cluster tagging system
- Student Enrollment API integration
- Official Receipt generation

### Priority 2 (Core Functionality)
- Cashiering workflow
- VAT/EWT calculation engine
- Budget Registry & validation
- Disbursement Voucher workflow

### Priority 3 (Reporting & Compliance)
- Report of Collections & Deposits (RCD)
- Trial Balance generation
- FAR 1 (Financial Accountability Report)
- Audit Trail immutability

---

## 📝 Notes for AI Development Agents

1. **All calculations must be deterministic** - No floating-point rounding errors
2. **Budget checks are HARD STOPS** - No warnings, only errors
3. **Posted transactions are immutable** - Require reversal entries
4. **Tax rates are configurable** - Must support annual updates
5. **Fund splitting is automatic** - Based on assessment line items
6. **Multi-bank deposits** - Same collection → multiple bank accounts
7. **Approval workflows are sequential** - Cannot skip Box B to reach Box C
8. **Printer formats are fixed** - OR and Check forms have specific layouts
9. **Audit trail is comprehensive** - Who, What, When, Why for every transaction
10. **System is zero-trust** - Every action requires explicit permission

---

**Last Updated:** February 3, 2026  
**Document Owner:** CvSU AIS Project Team  
**Review Cycle:** Weekly during development phases
