# GitHub Copilot Instructions for CvSU AIS Development

You are working on the **Cavite State University Accounting Information System (AIS)** built on Frappe Framework.

## 🎯 Primary Reference Documents

Before responding to any prompt, **ALWAYS** review these documents:

1. **[.github/PROJECT_CHARTER.md](.github/PROJECT_CHARTER.md)** - Business requirements, calculation scenarios, implementation phases
2. **[.github/DEVELOPMENT_GUIDELINES.md](.github/DEVELOPMENT_GUIDELINES.md)** - Coding standards, patterns, testing requirements
3. **[.github/AGENT_INSTRUCTIONS.md](.github/AGENT_INSTRUCTIONS.md)** - Implementation patterns and common pitfalls

## 🔒 Non-Negotiable Rules

### Financial Calculations
- **ALWAYS** use `Decimal` for money calculations, NEVER `float`
- **ALWAYS** round to 2 decimal places using `ROUND_HALF_UP`
- **ALWAYS** validate tax calculations match scenarios in PROJECT_CHARTER.md

### Budget Validation
- Budget checks are **HARD STOPS** - throw exceptions, not warnings
- **NEVER** allow transactions that exceed available budget
- Check budget availability BEFORE creating any obligation

### Data Integrity
- Posted documents are **IMMUTABLE** - require reversal entries
- **EVERY** transaction must have complete audit trail
- Debit must **ALWAYS** equal Credit in journal entries

### UACS Compliance
- All accounts must use valid UACS codes from Chart of Accounts
- Fund Cluster tagging is **MANDATORY**
- Cross-fund transactions require explicit validation

## 💻 Code Patterns to Follow

### DocType Controllers
```python
from decimal import Decimal
import frappe
from frappe.model.document import Document

class YourDocType(Document):
    def validate(self):
        self.validate_uacs_codes()
        self.validate_fund_cluster()
        self.calculate_amounts()
        self.validate_budget()
    
    def before_submit(self):
        self.validate_approval_chain()
    
    def on_submit(self):
        self.create_journal_entry()
        self.update_budget_utilization()
        self.log_audit_trail()
```

### Tax Calculations (Philippine BIR Rules)
```python
# VAT Registered Goods: 5% VAT + 1% EWT
gross = Decimal('112000.00')
net_of_vat = gross / Decimal('1.12')  # ₱100,000.00
vat = net_of_vat * Decimal('0.05')    # ₱5,000.00
ewt = net_of_vat * Decimal('0.01')    # ₱1,000.00
net_payable = gross - vat - ewt       # ₱106,000.00
```

### Budget Validation Pattern
```python
if requested_amount > available_balance:
    frappe.throw(
        f"Insufficient Budget. Available: ₱{available_balance:,.2f}",
        exc=frappe.InsufficientBudgetError
    )
```

## 📋 Implementation Phases

Current project is in **4 phases**:
1. **Phase 1 (Weeks 1-4):** Foundation & Master Data
2. **Phase 2 (Weeks 5-8):** Collections & Cashiering
3. **Phase 3 (Weeks 9-12):** Disbursements & Budget
4. **Phase 4 (Weeks 13+):** Reporting & Hardening

When implementing features, consider which phase they belong to and what prerequisites are needed.

## ✅ Before Suggesting Code

1. **Check** if it involves money → Use `Decimal`
2. **Check** if it affects budget → Add budget validation
3. **Check** if it creates journal entry → Ensure debit = credit
4. **Check** if it's a posted document → Make it immutable
5. **Check** UACS compliance → Validate account codes

## 🚫 Common Mistakes to Avoid

- ❌ Using `float` for currency amounts
- ❌ Allowing budget overdrafts
- ❌ Editing posted documents without reversal
- ❌ Skipping audit trail logging
- ❌ Trusting client-side calculations
- ❌ Hard-coding tax rates (they change annually)
- ❌ Allowing cross-fund transfers without validation

## 🎓 Framework Context

This is a **Frappe/ERPNext** project using:
- Python 3.11.6
- MariaDB 11.8
- Frappe Framework v15
- Docker containerized environment

Follow Frappe best practices but maintain Java Spring-like structure (services, repositories, DTOs) as documented in DEVELOPMENT_GUIDELINES.md.

## 💡 When Responding to Prompts

1. **Reference** the appropriate section from PROJECT_CHARTER.md or DEVELOPMENT_GUIDELINES.md
2. **Show** calculation logic with actual Philippine peso amounts
3. **Include** validation and error handling
4. **Demonstrate** audit trail logging
5. **Provide** test cases matching the scenarios

## 🔗 Quick Links

- Project Charter: `.github/PROJECT_CHARTER.md`
- Development Guidelines: `.github/DEVELOPMENT_GUIDELINES.md`
- Agent Instructions: `.github/AGENT_INSTRUCTIONS.md`
- Frappe Guide: `FRAPPE_GUIDE.md`
- Java to Frappe: `JAVA_TO_FRAPPE_GUIDE.md`

---

**Remember:** Every line of code must be audit-compliant and mathematically correct. When in doubt, refer to the calculation scenarios in PROJECT_CHARTER.md.
