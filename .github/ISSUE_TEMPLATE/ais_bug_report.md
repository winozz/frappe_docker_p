---
name: AIS Bug Report
about: Report a bug in the CvSU AIS system
title: '[AIS-BUG] '
labels: ais, bug, needs-triage
assignees: ''
---

## Bug Category
<!-- Check the affected phase/module -->
- [ ] Phase 1: Foundation & Master Data
- [ ] Phase 2: Collections & Cashiering
- [ ] Phase 3: Disbursements & Budget
- [ ] Phase 4: Reporting & Hardening

## Affected Module/DocType
- Module: 
- DocType: 
- Workflow: 

## Bug Description
<!-- Clear and concise description of the bug -->


## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Enter data '...'
4. See error

## Expected Behavior
<!-- What should have happened? -->


## Actual Behavior
<!-- What actually happened? -->


## Calculation Error (if applicable)
<!-- For financial bugs, show the incorrect vs correct calculation -->

**System Calculated:**
```python
# What the system did
gross_amount = 112000
net_payable = 112000 - 5000  # WRONG
```

**Should Calculate:**
```python
# What it should do
gross_amount = 112000
net_of_vat = gross_amount / 1.12
vat = net_of_vat * 0.05
ewt = net_of_vat * 0.01
net_payable = gross_amount - vat - ewt  # CORRECT
```

## Journal Entry Impact (if applicable)
<!-- If this bug affects journal entries, show the incorrect entry -->

**Incorrect Entry:**
```
Debit:  ...
Credit: ...
```

**Should Be:**
```
Debit:  ...
Credit: ...
```

## Data Integrity Impact
<!-- Does this bug compromise audit trail or data integrity? -->
- [ ] Critical - Data corruption or loss
- [ ] High - Incorrect financial calculations
- [ ] Medium - User workflow interrupted
- [ ] Low - UI/UX issue only

## Budget/Fund Impact
<!-- Does this bug affect budget validation or fund allocation? -->
- [ ] Allows overdraft when it shouldn't
- [ ] Blocks valid transaction
- [ ] Incorrect fund splitting
- [ ] Other: 
- [ ] N/A

## UACS Impact
<!-- Does this bug affect UACS Chart of Accounts? -->
- [ ] Yes - UACS code mapping incorrect
- [ ] No

## Environment
- Site: (e.g., ais.localhost, production)
- Frappe Version: 
- Browser: 
- User Role: 

## Screenshots/Error Messages
<!-- Attach screenshots or paste error messages -->

```
Error message here
```

## Audit Trail Check
<!-- Can this transaction be traced in audit logs? -->
- [ ] Yes - Audit trail is intact
- [ ] No - Audit trail is missing/corrupted
- [ ] Partial - Some information missing

## Financial Impact
<!-- What is the monetary impact of this bug? -->
- Variance Amount: ₱
- Affected Transactions: 
- Period: 

## COA Compliance Risk
<!-- Does this bug create a Commission on Audit finding? -->
- [ ] High - Will definitely be flagged
- [ ] Medium - Might be questioned
- [ ] Low - Minor issue
- [ ] None

## Urgency
- [ ] Critical - System down or data loss
- [ ] High - Blocks user workflow
- [ ] Medium - Workaround available
- [ ] Low - Minor inconvenience

## Workaround
<!-- Is there a temporary workaround? -->


## Additional Context
<!-- Add any other context about the problem -->
