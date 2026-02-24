# Agent Instruction Base for CvSU AIS Development

## 🤖 AI Agent Guidelines

When working on the CvSU Accounting Information System (AIS), AI agents and developers must follow these instructions:

---

## Core Principles

### 1. Financial Calculations Must Be Deterministic

```python
# ✅ CORRECT - Use Decimal for all money calculations
from decimal import Decimal, ROUND_HALF_UP

gross_amount = Decimal('112000.00')
net_of_vat = (gross_amount / Decimal('1.12')).quantize(
    Decimal('0.01'), rounding=ROUND_HALF_UP
)

# ❌ WRONG - Never use float for money
gross_amount = 112000.00  # Floating point errors!
net_of_vat = gross_amount / 1.12  # Will cause rounding issues
```

### 2. Budget Validation is a HARD STOP

```python
# Budget checks throw exceptions, not warnings
if requested_amount > available_balance:
    frappe.throw(
        f"Insufficient Budget. Available: ₱{available_balance:,.2f}",
        exc=frappe.InsufficientBudgetError
    )
    # Execution stops here - user cannot proceed
```

### 3. Posted Documents are Immutable

```python
# ❌ NEVER allow direct editing of posted documents
def on_update_after_submit(self):
    frappe.throw("Cannot modify posted voucher. Create reversal entry.")

# ✅ CORRECT - Require reversal entries
def create_reversal_entry(original_doc):
    reversal = frappe.copy_doc(original_doc)
    reversal.is_reversal = 1
    # Flip all debits/credits
    for item in reversal.items:
        item.debit, item.credit = item.credit, item.debit
    return reversal
```

### 4. Every Transaction Needs Audit Trail

```python
def log_audit_trail(self):
    """Log all critical actions"""
    frappe.get_doc({
        "doctype": "Audit Log",
        "document_type": self.doctype,
        "document_name": self.name,
        "action": "Submit",
        "user": frappe.session.user,
        "timestamp": frappe.utils.now(),
        "before_value": self.get_before_save(),
        "after_value": self.as_dict(),
        "ip_address": frappe.local.request_ip
    }).insert(ignore_permissions=True)
```

---

## Calculation Scenarios Reference

### Tax Calculation Template

```python
def calculate_philippine_taxes(gross_amount: Decimal, supplier_type: str, txn_type: str):
    """
    Standard tax calculation for CvSU AIS
    
    Args:
        gross_amount: Total amount including VAT
        supplier_type: 'vat_registered' or 'non_vat'
        txn_type: 'goods' (1% EWT), 'services' (2% EWT), 
                  'rentals' (5% EWT), 'professional' (10% EWT)
    """
    VAT_DIVISOR = Decimal('1.12')
    VAT_RATE = Decimal('0.05')  # 5% Final VAT for government
    
    EWT_RATES = {
        'goods': Decimal('0.01'),
        'services': Decimal('0.02'),
        'rentals': Decimal('0.05'),
        'professional': Decimal('0.10')
    }
    
    # Step 1: Extract net of VAT (tax base)
    if supplier_type == 'vat_registered':
        net_of_vat = (gross_amount / VAT_DIVISOR).quantize(Decimal('0.01'))
        vat = (net_of_vat * VAT_RATE).quantize(Decimal('0.01'))
    else:
        net_of_vat = gross_amount
        vat = Decimal('0.00')
    
    # Step 2: Calculate EWT
    ewt = (net_of_vat * EWT_RATES[txn_type]).quantize(Decimal('0.01'))
    
    # Step 3: Net payable
    net_payable = gross_amount - vat - ewt
    
    return {
        'tax_base': net_of_vat,
        'vat': vat,
        'ewt': ewt,
        'net_payable': net_payable
    }
```

### Fund Splitting Template

```python
def split_collection_by_fund(assessment_items: list, total_paid: Decimal):
    """
    Distribute student payment across multiple funds
    
    Args:
        assessment_items: List of assessment line items
        total_paid: Total amount received
    
    Returns:
        dict: Fund-wise breakdown for deposit
    """
    fund_allocations = {}
    
    for item in assessment_items:
        fund = item.fund_cluster
        amount = Decimal(str(item.amount))
        
        if fund not in fund_allocations:
            fund_allocations[fund] = {
                'items': [],
                'total': Decimal('0.00'),
                'bank_account': get_fund_bank_account(fund)
            }
        
        fund_allocations[fund]['items'].append({
            'description': item.fee_description,
            'amount': amount
        })
        fund_allocations[fund]['total'] += amount
    
    # Validate total matches
    total_allocated = sum([f['total'] for f in fund_allocations.values()])
    if total_allocated != total_paid:
        frappe.throw(
            f"Allocation mismatch. Paid: ₱{total_paid}, "
            f"Allocated: ₱{total_allocated}"
        )
    
    return fund_allocations
```

### Budget Check Template

```python
def validate_budget_availability(fund, account, amount, fiscal_year):
    """
    Check if budget is available before creating obligation
    
    Raises:
        frappe.InsufficientBudgetError: If budget is insufficient
    """
    budget = frappe.db.get_value(
        "Budget Registry",
        filters={
            "fund_cluster": fund,
            "account": account,
            "fiscal_year": fiscal_year
        },
        fieldname=["allotment", "obligations", "available_balance"],
        as_dict=True
    )
    
    if not budget:
        frappe.throw(f"No budget allocated for {account} in {fund}")
    
    available = Decimal(str(budget.available_balance))
    requested = Decimal(str(amount))
    
    if requested > available:
        frappe.throw(
            f"Insufficient Budget for {account}\n"
            f"Available: ₱{available:,.2f}\n"
            f"Requested: ₱{requested:,.2f}\n"
            f"Shortfall: ₱{(requested - available):,.2f}",
            exc=frappe.InsufficientBudgetError
        )
    
    return True
```

---

## Required Validations

### Every Financial DocType MUST validate:

1. **UACS Code Validity**
```python
def validate_uacs_code(account):
    if not frappe.db.exists("Chart of Accounts", {"uacs_code": account}):
        frappe.throw(f"Invalid UACS Code: {account}")
```

2. **Fund Cluster Tagging**
```python
def validate_fund_cluster(account, expected_fund):
    actual_fund = frappe.db.get_value("Chart of Accounts", account, "fund_cluster")
    if actual_fund != expected_fund:
        frappe.throw(f"Account {account} belongs to {actual_fund}, not {expected_fund}")
```

3. **Approval Workflow Sequence**
```python
def validate_approval_sequence(self):
    if self.box_c_approved_by and not self.box_b_approved_by:
        frappe.throw("Cannot approve Box C without Box B")
    if self.box_b_approved_by and not self.box_a_approved_by:
        frappe.throw("Cannot approve Box B without Box A")
```

4. **Debit-Credit Balance**
```python
def validate_journal_balance(self):
    total_debit = sum([Decimal(str(d.debit)) for d in self.accounts])
    total_credit = sum([Decimal(str(d.credit)) for d in self.accounts])
    
    if total_debit != total_credit:
        frappe.throw(
            f"Journal Entry not balanced. "
            f"Debit: ₱{total_debit:,.2f}, Credit: ₱{total_credit:,.2f}"
        )
```

---

## Integration Requirements

### Student Enrollment System API

```python
@frappe.whitelist()
def fetch_student_assessment(student_id: str):
    """
    Fetch student assessment from enrollment system
    
    Returns:
        dict: {
            'student_id': str,
            'student_name': str,
            'program': str,
            'year_level': str,
            'assessment_items': [
                {
                    'fee_code': str,
                    'description': str,
                    'amount': Decimal,
                    'fund_cluster': str
                }
            ],
            'total_assessment': Decimal,
            'payments_made': Decimal,
            'balance': Decimal
        }
    """
    # Call external API
    api_url = frappe.get_site_config().get('enrollment_api_url')
    response = requests.get(f"{api_url}/student/{student_id}/assessment")
    
    if response.status_code != 200:
        frappe.throw(f"Student {student_id} not found in enrollment system")
    
    data = response.json()
    
    # Validate response structure
    required_fields = ['student_id', 'student_name', 'assessment_items']
    for field in required_fields:
        if field not in data:
            frappe.throw(f"Invalid API response: Missing field '{field}'")
    
    return data
```

---

## Naming Conventions

### DocTypes
- **Singular, Title Case:** `Official Receipt`, `Disbursement Voucher`
- **No abbreviations in DocType names:** ❌ `DV`, ✅ `Disbursement Voucher`

### Fields
- **Snake case:** `gross_amount`, `net_payable`, `fund_cluster`
- **Prefix boolean fields:** `is_posted`, `has_approval`, `is_cancelled`
- **Suffix amounts:** `amount`, `total`, `balance`

### Methods
- **Verb-noun pattern:** `calculate_taxes()`, `validate_budget()`, `create_journal_entry()`
- **Prefix validators:** `validate_*()`, `check_*()`, `verify_*`

---

## Error Handling

### Use Specific Exceptions

```python
# Define custom exceptions
class InsufficientBudgetError(frappe.ValidationError):
    pass

class InvalidUACSCodeError(frappe.ValidationError):
    pass

class ApprovalSequenceError(frappe.ValidationError):
    pass

# Use them appropriately
try:
    validate_budget_availability(...)
except InsufficientBudgetError as e:
    # Handle budget shortage
    frappe.msgprint(str(e), indicator='red', alert=True)
except InvalidUACSCodeError as e:
    # Handle UACS error
    frappe.log_error(str(e), "UACS Validation Error")
```

---

## Testing Scenarios

### Required Test Cases for Every Financial Module

1. **Happy Path Test**
```python
def test_normal_disbursement():
    # Create voucher with valid data
    doc = create_test_voucher(gross_amount=112000, supplier_type='vat_registered')
    doc.submit()
    
    # Verify calculations
    assert doc.net_of_vat == 100000
    assert doc.vat_amount == 5000
    assert doc.ewt_amount == 1000
    assert doc.net_payable == 106000
```

2. **Budget Insufficient Test**
```python
def test_budget_block():
    # Set budget to low amount
    set_budget(fund='164', account='5020101000', amount=10000)
    
    # Attempt large purchase
    doc = create_test_voucher(gross_amount=50000)
    
    # Should raise error
    with pytest.raises(frappe.InsufficientBudgetError):
        doc.submit()
```

3. **Invalid Input Test**
```python
def test_invalid_uacs_code():
    doc = create_test_voucher()
    doc.items[0].account = "INVALID-CODE"
    
    with pytest.raises(frappe.ValidationError):
        doc.save()
```

4. **Approval Sequence Test**
```python
def test_approval_sequence():
    doc = create_test_voucher()
    doc.box_a_approved_by = None
    doc.box_c_approved_by = "user@example.com"
    
    with pytest.raises(frappe.ValidationError):
        doc.submit()
```

---

## Performance Guidelines

### Database Queries

```python
# ❌ WRONG - N+1 query problem
for item in items:
    account = frappe.get_doc("Chart of Accounts", item.account)
    fund = account.fund_cluster

# ✅ CORRECT - Batch query
accounts = frappe.get_all(
    "Chart of Accounts",
    filters={"name": ["in", [i.account for i in items]]},
    fields=["name", "fund_cluster"]
)
account_map = {a.name: a for a in accounts}
```

### Caching

```python
# Cache UACS structure (changes rarely)
@frappe.cache()
def get_uacs_tree():
    return frappe.db.sql("""
        SELECT uacs_code, account_title, parent_account
        FROM `tabChart of Accounts`
        ORDER BY uacs_code
    """, as_dict=True)
```

---

## Security Checklist

- [ ] All API endpoints use `@frappe.whitelist()`
- [ ] Sensitive operations check `frappe.has_permission()`
- [ ] User input is validated and sanitized
- [ ] SQL queries use parameterized statements
- [ ] File uploads are restricted by type and size
- [ ] Audit trail captures user, IP, and timestamp
- [ ] Password fields are never logged
- [ ] API keys are stored in site_config, not code

---

## Deployment Verification

Before marking a phase complete, verify:

```python
def verify_phase_completion(phase_number):
    """
    Automated verification of phase completion criteria
    """
    checklist = {
        1: verify_phase_1,
        2: verify_phase_2,
        3: verify_phase_3,
        4: verify_phase_4
    }
    
    return checklist[phase_number]()

def verify_phase_1():
    # UACS Tree 100% accurate
    uacs_count = frappe.db.count("Chart of Accounts")
    manual_count = get_manual_uacs_count()
    assert uacs_count == manual_count, "UACS count mismatch"
    
    # Fetch Assessment works
    test_student = fetch_student_assessment("TEST-001")
    assert test_student['student_id'] == "TEST-001"
    
    return True

def verify_phase_2():
    # 100 consecutive transactions without error
    errors = frappe.get_all("Error Log", 
        filters={"creation": [">", "2026-02-01"]},
        limit=100
    )
    assert len(errors) == 0, "Errors found in last 100 transactions"
    
    # RCD balances for 5 days
    for day in range(5):
        rcd_balance = check_rcd_balance(day)
        assert rcd_balance == 0, f"RCD variance on day {day}"
    
    return True
```

---

## Common Pitfalls to Avoid

### ❌ Don't Do This

```python
# Trusting client-calculated totals
@frappe.whitelist()
def save_voucher(data):
    doc = frappe.get_doc(data)  # Don't trust client data!
    doc.save()  # Net payable might be wrong

# Using string concatenation for SQL
account = "5020101000"
sql = f"SELECT * FROM `tabBudget` WHERE account = '{account}'"  # SQL injection risk!

# Ignoring decimal precision
amount = 112000 / 1.12  # Float error
vat = amount * 0.05  # Compounding error
```

### ✅ Do This Instead

```python
# Recalculate on server
@frappe.whitelist()
def save_voucher(data):
    doc = frappe.get_doc(data)
    doc.calculate_taxes()  # Recalculate server-side
    doc.save()

# Use parameterized queries
account = "5020101000"
sql = "SELECT * FROM `tabBudget` WHERE account = %(account)s"
result = frappe.db.sql(sql, {"account": account})

# Use Decimal for money
from decimal import Decimal
amount = Decimal('112000') / Decimal('1.12')
vat = amount * Decimal('0.05')
```

---

**Agent Reminder:** When implementing any CvSU AIS feature, always reference:
1. [PROJECT_CHARTER.md](.github/PROJECT_CHARTER.md) - Business requirements
2. [DEVELOPMENT_GUIDELINES.md](.github/DEVELOPMENT_GUIDELINES.md) - Code standards
3. This file - Implementation patterns

**Last Updated:** February 3, 2026
