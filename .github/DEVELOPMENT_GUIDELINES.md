# CvSU AIS Development Guidelines

## 🎯 Development Principles

### 1. Audit Compliance First
- **Every transaction MUST be traceable**
- Immutable records after posting
- Complete audit trail (Who, What, When, Why)
- No soft deletes for posted documents

### 2. Zero-Trust Calculation
- All financial calculations must be explicit and deterministic
- No assumptions or defaults for critical values
- Validate inputs before processing
- Use Decimal types, never floats for money

### 3. Budget is Sacred
- Budget checks are HARD STOPS, not warnings
- No transaction can exceed available balance
- Real-time budget utilization tracking
- Multi-level approval cannot bypass budget limits

### 4. Fund Integrity
- Fund tagging is mandatory
- Cross-fund transfers require special approval
- Trust funds are isolated from general funds
- Fund splitting must be automatic and accurate

---

## 📁 Project Structure (AIS App)

```
apps/ais/
├── ais/
│   ├── ais/
│   │   ├── doctype/           # All DocTypes
│   │   │   ├── chart_of_accounts/
│   │   │   ├── fund_cluster/
│   │   │   ├── official_receipt/
│   │   │   ├── collection_entry/
│   │   │   ├── disbursement_voucher/
│   │   │   ├── budget_registry/
│   │   │   └── ...
│   │   ├── services/          # Business logic layer
│   │   │   ├── tax_service.py
│   │   │   ├── budget_service.py
│   │   │   ├── fund_service.py
│   │   │   └── ...
│   │   ├── repositories/      # Data access layer
│   │   │   ├── account_repository.py
│   │   │   ├── budget_repository.py
│   │   │   └── ...
│   │   ├── api/              # REST API endpoints
│   │   │   ├── student_api.py
│   │   │   ├── collection_api.py
│   │   │   ├── disbursement_api.py
│   │   │   └── swagger.py
│   │   ├── validators/       # Input validation
│   │   │   ├── uacs_validator.py
│   │   │   ├── fund_validator.py
│   │   │   └── ...
│   │   ├── utils/           # Utility functions
│   │   │   ├── currency.py
│   │   │   ├── printer.py
│   │   │   └── ...
│   │   └── config/
│   │       └── desktop.py
│   ├── hooks.py            # App configuration
│   ├── requirements.txt    # Python dependencies
│   └── public/            # Static files
└── tests/                 # Unit tests
```

---

## 💻 Coding Standards

### DocType Controller Pattern

```python
import frappe
from frappe.model.document import Document
from decimal import Decimal
from ais.services.tax_service import TaxService
from ais.validators.budget_validator import BudgetValidator

class DisbursementVoucher(Document):
    """
    Disbursement Voucher with VAT/EWT calculation and budget validation
    """
    
    def validate(self):
        """Called before saving (draft or submit)"""
        self.validate_uacs_codes()
        self.validate_fund_cluster()
        self.calculate_taxes()
        self.validate_budget()
    
    def before_submit(self):
        """Called before submitting (making immutable)"""
        self.validate_approval_chain()
        self.reserve_budget()
    
    def on_submit(self):
        """Called after successful submission"""
        self.create_journal_entry()
        self.update_budget_utilization()
        self.log_audit_trail()
    
    def on_cancel(self):
        """Called when document is cancelled"""
        self.create_reversal_entry()
        self.release_budget_reservation()
    
    # === Validation Methods ===
    
    def validate_uacs_codes(self):
        """Ensure all accounts use valid UACS codes"""
        for item in self.items:
            if not frappe.db.exists("Chart of Accounts", item.account):
                frappe.throw(f"Invalid UACS Account: {item.account}")
    
    def validate_fund_cluster(self):
        """Ensure fund cluster is properly tagged"""
        if not self.fund_cluster:
            frappe.throw("Fund Cluster is mandatory")
        
        # Validate all accounts belong to same fund
        for item in self.items:
            account = frappe.get_doc("Chart of Accounts", item.account)
            if account.fund_cluster != self.fund_cluster:
                frappe.throw(
                    f"Account {item.account} does not belong to Fund {self.fund_cluster}"
                )
    
    def calculate_taxes(self):
        """Calculate VAT and EWT using TaxService"""
        tax_service = TaxService()
        
        for item in self.items:
            result = tax_service.calculate_taxes(
                gross_amount=Decimal(str(item.gross_amount)),
                supplier_type=self.supplier_type,
                transaction_type=item.transaction_type
            )
            
            item.net_of_vat = float(result['net_of_vat'])
            item.vat_amount = float(result['vat'])
            item.ewt_amount = float(result['ewt'])
            item.net_payable = float(result['net_payable'])
        
        self.update_totals()
    
    def validate_budget(self):
        """Validate against budget registry - HARD STOP if insufficient"""
        validator = BudgetValidator()
        
        for item in self.items:
            available = validator.get_available_balance(
                fund_cluster=self.fund_cluster,
                account=item.account,
                fiscal_year=self.fiscal_year
            )
            
            if Decimal(str(item.gross_amount)) > available:
                frappe.throw(
                    f"Insufficient Budget for {item.account}. "
                    f"Available: ₱{available:,.2f}, "
                    f"Requested: ₱{item.gross_amount:,.2f}",
                    exc=frappe.InsufficientBudgetError
                )
    
    def validate_approval_chain(self):
        """Ensure Box A → Box B → Box C sequence"""
        if not self.box_a_approved_by:
            frappe.throw("Box A approval required")
        
        if self.box_c_approved_by and not self.box_b_approved_by:
            frappe.throw("Cannot approve Box C without Box B approval")
    
    # === Accounting Methods ===
    
    def create_journal_entry(self):
        """Create corresponding Journal Entry"""
        je = frappe.get_doc({
            "doctype": "Journal Entry",
            "posting_date": self.posting_date,
            "voucher_type": "Disbursement",
            "accounts": []
        })
        
        # Debit: Expense/Asset accounts
        for item in self.items:
            je.append("accounts", {
                "account": item.account,
                "debit_in_account_currency": item.gross_amount,
                "fund_cluster": self.fund_cluster
            })
        
        # Credit: Tax accounts
        total_vat = sum([Decimal(str(item.vat_amount)) for item in self.items])
        total_ewt = sum([Decimal(str(item.ewt_amount)) for item in self.items])
        
        if total_vat > 0:
            je.append("accounts", {
                "account": "2010301000 - Due to BIR - VAT",
                "credit_in_account_currency": float(total_vat)
            })
        
        if total_ewt > 0:
            je.append("accounts", {
                "account": "2010302000 - Due to BIR - EWT",
                "credit_in_account_currency": float(total_ewt)
            })
        
        # Credit: Cash/Bank
        je.append("accounts", {
            "account": self.bank_account,
            "credit_in_account_currency": self.net_payable_total
        })
        
        je.insert()
        je.submit()
        
        self.journal_entry = je.name
    
    def update_budget_utilization(self):
        """Update Budget Registry with obligation"""
        for item in self.items:
            budget = frappe.get_doc("Budget Registry", {
                "fund_cluster": self.fund_cluster,
                "account": item.account,
                "fiscal_year": self.fiscal_year
            })
            
            budget.obligations += Decimal(str(item.gross_amount))
            budget.available_balance = budget.allotment - budget.obligations
            budget.save()
    
    # === Helper Methods ===
    
    def update_totals(self):
        """Recalculate document totals"""
        self.gross_total = sum([Decimal(str(i.gross_amount)) for i in self.items])
        self.vat_total = sum([Decimal(str(i.vat_amount)) for i in self.items])
        self.ewt_total = sum([Decimal(str(i.ewt_amount)) for i in self.items])
        self.net_payable_total = sum([Decimal(str(i.net_payable)) for i in self.items])
```

---

## 🧮 Tax Calculation Service

```python
# ais/services/tax_service.py

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict
import frappe

class TaxService:
    """
    Centralized tax calculation following Philippine BIR rules
    """
    
    VAT_RATE = Decimal('0.05')  # 5% Final VAT (Government)
    VAT_DIVISOR = Decimal('1.12')  # To extract net of VAT
    
    EWT_RATES = {
        'goods': Decimal('0.01'),      # 1% for goods
        'services': Decimal('0.02'),   # 2% for services
        'rentals': Decimal('0.05'),    # 5% for rentals
        'professional': Decimal('0.10') # 10% for professional fees
    }
    
    def calculate_taxes(
        self, 
        gross_amount: Decimal, 
        supplier_type: str,
        transaction_type: str
    ) -> Dict[str, Decimal]:
        """
        Calculate VAT and EWT from gross amount
        
        Args:
            gross_amount: Total amount (VAT inclusive)
            supplier_type: 'vat_registered' or 'non_vat'
            transaction_type: 'goods', 'services', 'rentals', 'professional'
        
        Returns:
            dict with keys: net_of_vat, vat, ewt, net_payable
        """
        # Validate inputs
        if gross_amount <= 0:
            frappe.throw("Gross amount must be positive")
        
        if supplier_type not in ['vat_registered', 'non_vat']:
            frappe.throw(f"Invalid supplier type: {supplier_type}")
        
        if transaction_type not in self.EWT_RATES:
            frappe.throw(f"Invalid transaction type: {transaction_type}")
        
        # Calculate net of VAT (tax base)
        if supplier_type == 'vat_registered':
            net_of_vat = (gross_amount / self.VAT_DIVISOR).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            vat = (net_of_vat * self.VAT_RATE).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        else:
            net_of_vat = gross_amount
            vat = Decimal('0.00')
        
        # Calculate EWT
        ewt_rate = self.EWT_RATES[transaction_type]
        ewt = (net_of_vat * ewt_rate).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        # Calculate net payable
        net_payable = gross_amount - vat - ewt
        
        return {
            'net_of_vat': net_of_vat,
            'vat': vat,
            'ewt': ewt,
            'net_payable': net_payable
        }
```

---

## ✅ Testing Requirements

### Unit Test Example

```python
# tests/test_tax_service.py

import unittest
from decimal import Decimal
from ais.services.tax_service import TaxService

class TestTaxService(unittest.TestCase):
    
    def setUp(self):
        self.tax_service = TaxService()
    
    def test_vat_registered_goods(self):
        """Test Scenario A: VAT Registered Goods"""
        result = self.tax_service.calculate_taxes(
            gross_amount=Decimal('112000.00'),
            supplier_type='vat_registered',
            transaction_type='goods'
        )
        
        self.assertEqual(result['net_of_vat'], Decimal('100000.00'))
        self.assertEqual(result['vat'], Decimal('5000.00'))
        self.assertEqual(result['ewt'], Decimal('1000.00'))
        self.assertEqual(result['net_payable'], Decimal('106000.00'))
    
    def test_vat_registered_services(self):
        """Test Scenario B: VAT Registered Services"""
        result = self.tax_service.calculate_taxes(
            gross_amount=Decimal('56000.00'),
            supplier_type='vat_registered',
            transaction_type='services'
        )
        
        self.assertEqual(result['net_of_vat'], Decimal('50000.00'))
        self.assertEqual(result['vat'], Decimal('2500.00'))
        self.assertEqual(result['ewt'], Decimal('1000.00'))  # 2% for services
        self.assertEqual(result['net_payable'], Decimal('52500.00'))
    
    def test_non_vat_supplier(self):
        """Test Non-VAT Supplier (no VAT extraction)"""
        result = self.tax_service.calculate_taxes(
            gross_amount=Decimal('100000.00'),
            supplier_type='non_vat',
            transaction_type='goods'
        )
        
        self.assertEqual(result['net_of_vat'], Decimal('100000.00'))
        self.assertEqual(result['vat'], Decimal('0.00'))
        self.assertEqual(result['ewt'], Decimal('1000.00'))
        self.assertEqual(result['net_payable'], Decimal('99000.00'))
```

---

## 🔒 Security Guidelines

### 1. Permission Rules
```python
# In DocType JSON
{
    "permissions": [
        {
            "role": "Cashier",
            "create": 1,
            "read": 1,
            "write": 1,
            "submit": 1,  # Can post transactions
            "cancel": 0,  # Cannot cancel
            "delete": 0   # Cannot delete
        },
        {
            "role": "Accountant",
            "create": 1,
            "read": 1,
            "write": 1,
            "submit": 1,
            "cancel": 1,  # Can cancel
            "delete": 0   # Still cannot delete
        }
    ]
}
```

### 2. Server-Side Validation Only
```python
# NEVER trust client-side data
@frappe.whitelist()
def create_disbursement(data):
    # Validate on server
    if not isinstance(data, dict):
        frappe.throw("Invalid data format")
    
    # Re-calculate all amounts (don't trust client)
    tax_service = TaxService()
    result = tax_service.calculate_taxes(...)
    
    # Use server-calculated values, not client values
    doc.net_payable = result['net_payable']
```

---

## 📊 Reporting Standards

### Financial Report Structure

```python
# ais/api/reports.py

@frappe.whitelist()
def generate_trial_balance(fiscal_year, fund_cluster=None):
    """
    Generate Trial Balance with UACS grouping
    """
    filters = {"fiscal_year": fiscal_year}
    if fund_cluster:
        filters["fund_cluster"] = fund_cluster
    
    data = frappe.db.sql("""
        SELECT 
            coa.uacs_code,
            coa.account_title,
            coa.fund_cluster,
            SUM(CASE WHEN je.debit > 0 THEN je.debit ELSE 0 END) as total_debit,
            SUM(CASE WHEN je.credit > 0 THEN je.credit ELSE 0 END) as total_credit
        FROM 
            `tabChart of Accounts` coa
        LEFT JOIN 
            `tabJournal Entry Account` je ON je.account = coa.name
        WHERE
            je.fiscal_year = %(fiscal_year)s
            {fund_filter}
        GROUP BY 
            coa.uacs_code, coa.account_title, coa.fund_cluster
        ORDER BY 
            coa.uacs_code
    """.format(
        fund_filter="AND coa.fund_cluster = %(fund_cluster)s" if fund_cluster else ""
    ), filters, as_dict=True)
    
    # Validate balance
    total_debit = sum([Decimal(str(row.total_debit)) for row in data])
    total_credit = sum([Decimal(str(row.total_credit)) for row in data])
    
    variance = total_debit - total_credit
    if variance != 0:
        frappe.log_error(
            f"Trial Balance Variance: ₱{variance:,.2f}",
            "Trial Balance Error"
        )
    
    return {
        "data": data,
        "total_debit": float(total_debit),
        "total_credit": float(total_credit),
        "variance": float(variance),
        "is_balanced": variance == 0
    }
```

---

## 🚀 Deployment Checklist

### Before Each Phase Deployment

- [ ] All unit tests passing
- [ ] Integration tests completed
- [ ] Tax calculations verified against 10 manual samples
- [ ] Budget validation tested (both allow and block scenarios)
- [ ] Audit trail verified (can trace every transaction)
- [ ] Role permissions tested
- [ ] UACS codes validated against COA Manual
- [ ] Printer formats tested with actual forms
- [ ] Database backup completed
- [ ] Rollback plan documented

---

## 📝 Documentation Requirements

Every DocType must have:
1. **Docstring** explaining purpose
2. **Field descriptions** in JSON
3. **Validation rules** documented
4. **Sample data** for testing
5. **User guide** entry

Every API endpoint must have:
1. **Swagger documentation**
2. **Request/response examples**
3. **Error codes explained**
4. **Rate limiting rules**

---

## 🐛 Debugging Guidelines

### Enable Developer Mode
```python
# In site_config.json
{
    "developer_mode": 1,
    "logging": 2  # Verbose logging
}
```

### Add Debug Logging
```python
import frappe

frappe.log_error(
    title="Budget Validation Debug",
    message=f"Available: {available}, Requested: {requested}"
)
```

### Test in Bench Console
```bash
bench --site ais.localhost console

>>> from ais.services.tax_service import TaxService
>>> ts = TaxService()
>>> ts.calculate_taxes(Decimal('112000'), 'vat_registered', 'goods')
```

---

**Last Updated:** February 3, 2026  
**Review Required:** Before each phase deployment
