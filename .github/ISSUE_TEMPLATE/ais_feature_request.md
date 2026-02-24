---
name: AIS Feature Request
about: Request a new feature or module for the CvSU AIS system
title: '[AIS-FEATURE] '
labels: ais, enhancement, needs-review
assignees: ''
---

## Feature Category
<!-- Check the relevant phase -->
- [ ] Phase 1: Foundation & Master Data
- [ ] Phase 2: Collections & Cashiering
- [ ] Phase 3: Disbursements & Budget
- [ ] Phase 4: Reporting & Hardening

## Module/DocType
<!-- Which module does this feature belong to? -->
- Module: 
- Affected DocTypes: 

## Feature Description
<!-- Clear and concise description of what you want to happen -->


## Business Justification
<!-- Why is this feature necessary? Which user role needs this? -->
- **User Role:** (e.g., Cashier, Budget Officer, Accountant)
- **Business Need:** 
- **Expected Outcome:** 

## Calculation Logic (if applicable)
<!-- For financial features, provide the exact calculation formula -->

```python
# Example calculation logic
gross_amount = 112000
net_of_vat = gross_amount / 1.12
vat = net_of_vat * 0.05
ewt = net_of_vat * 0.01
net_payable = gross_amount - vat - ewt
```

## Journal Entry Impact (if applicable)
<!-- For accounting features, show the expected journal entry -->

```
Debit:  Account Name  ₱ Amount
Credit: Account Name  ₱ Amount
```

## UACS Compliance
<!-- Does this feature affect UACS Chart of Accounts? -->
- [ ] Yes - Specify UACS codes affected: 
- [ ] No

## Fund Cluster Impact
<!-- Which fund clusters are affected? -->
- [ ] Fund 164 (General Fund)
- [ ] Trust Fund
- [ ] Other: 

## Budget Impact
<!-- Does this feature require budget validation? -->
- [ ] Yes - Budget check required before processing
- [ ] No - No budget validation needed

## Integration Requirements
<!-- Does this feature require external system integration? -->
- [ ] Student Enrollment System
- [ ] Banking System
- [ ] Other: 
- [ ] None

## Acceptance Criteria
<!-- Define what "done" means for this feature -->
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Audit Trail Requirements
<!-- What must be logged for audit purposes? -->
- [ ] User who performed action
- [ ] Timestamp
- [ ] Before/After values
- [ ] Approval chain
- [ ] Other: 

## Priority
- [ ] Critical (Blocks deployment)
- [ ] High (Required for phase completion)
- [ ] Medium (Important but not blocking)
- [ ] Low (Nice to have)

## Additional Context
<!-- Add any other context, screenshots, or examples -->
