# Java Spring → Frappe Framework: Migration Guide

## 🎯 Framework Comparison

| Java Spring Boot | Frappe Framework | Notes |
|-----------------|------------------|-------|
| Spring Boot | Frappe | Full-stack web framework |
| Gradle / Maven | Bench CLI | Build & dependency management |
| JPA / Hibernate | Frappe ORM | Database abstraction |
| Spring MVC | Frappe Controllers | Request handling |
| Spring Data Repositories | DocType API | Data access layer |
| @RestController | Whitelisted methods | API endpoints |
| application.properties | site_config.json, hooks.py | Configuration |
| JUnit | unittest / frappe.tests | Testing framework |

## 📁 Project Structure Comparison

### Java Spring (Typical Structure)
```
myproject/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/company/project/
│   │   │       ├── controller/
│   │   │       ├── service/
│   │   │       ├── repository/
│   │   │       ├── model/
│   │   │       └── dto/
│   │   └── resources/
│   │       ├── application.properties
│   │       └── static/
│   └── test/
├── build.gradle
└── settings.gradle
```

### Frappe (Equivalent Structure)
```
apps/ais/
├── ais/
│   ├── ais/
│   │   ├── doctype/          # Models (like @Entity classes)
│   │   │   └── customer/
│   │   │       ├── customer.json      # Schema (like JPA annotations)
│   │   │       ├── customer.py        # Controller (like @Service)
│   │   │       └── customer.js        # Frontend logic
│   │   ├── api.py            # REST Controllers (like @RestController)
│   │   ├── utils.py          # Utility classes
│   │   └── config/
│   │       └── desktop.py
│   ├── hooks.py              # Configuration (like application.properties)
│   ├── requirements.txt      # Dependencies (like build.gradle)
│   └── public/               # Static files
└── tests/                    # Unit tests (like src/test)
```

## 🔄 Concept Mapping

### 1. Entity/Model Definition

**Java Spring (JPA Entity):**
```java
@Entity
@Table(name = "customers")
public class Customer {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String customerName;
    
    @Column(unique = true)
    private String email;
    
    @OneToMany(mappedBy = "customer", cascade = CascadeType.ALL)
    private List<Order> orders;
    
    @CreatedDate
    private LocalDateTime createdAt;
    
    @LastModifiedDate
    private LocalDateTime updatedAt;
    
    // Getters, setters, constructors
}
```

**Frappe (DocType):**
```python
# customer.json (created via UI or code)
{
    "name": "Customer",
    "module": "AIS",
    "autoname": "field:customer_name",
    "fields": [
        {
            "fieldname": "customer_name",
            "fieldtype": "Data",
            "reqd": 1,
            "label": "Customer Name"
        },
        {
            "fieldname": "email",
            "fieldtype": "Data",
            "unique": 1,
            "label": "Email"
        }
    ],
    "track_changes": 1  # Like @Version or audit
}

# customer.py (Controller)
import frappe
from frappe.model.document import Document

class Customer(Document):
    # Equivalent to @PrePersist / @PreUpdate
    def validate(self):
        self.validate_email()
    
    def validate_email(self):
        if not self.email or "@" not in self.email:
            frappe.throw("Invalid email address")
    
    # Equivalent to @PostPersist
    def on_submit(self):
        self.create_welcome_email()
    
    # Custom business logic
    def get_total_orders(self):
        return frappe.db.count("Sales Order", {"customer": self.name})
```

### 2. Repository / Data Access

**Java Spring (Repository):**
```java
@Repository
public interface CustomerRepository extends JpaRepository<Customer, Long> {
    Optional<Customer> findByEmail(String email);
    List<Customer> findByCustomerNameContaining(String name);
    
    @Query("SELECT c FROM Customer c WHERE c.status = :status")
    List<Customer> findActiveCustomers(@Param("status") String status);
}
```

**Frappe (Database API):**
```python
# No need for separate repository classes
import frappe

# Get single record
customer = frappe.get_doc("Customer", "CUST-001")
customer = frappe.db.get_value("Customer", {"email": "test@example.com"}, "*")

# Get multiple records
customers = frappe.get_all("Customer", 
    filters={"customer_name": ["like", "%John%"]},
    fields=["name", "email", "phone"]
)

# Raw SQL (like @Query)
active_customers = frappe.db.sql("""
    SELECT name, email FROM `tabCustomer` 
    WHERE status = %(status)s
""", {"status": "Active"}, as_dict=True)

# Count
count = frappe.db.count("Customer", {"status": "Active"})

# Exists
exists = frappe.db.exists("Customer", "CUST-001")
```

### 3. Service Layer

**Java Spring (Service):**
```java
@Service
@Transactional
public class CustomerService {
    @Autowired
    private CustomerRepository customerRepository;
    
    public CustomerDTO createCustomer(CustomerDTO dto) {
        Customer customer = new Customer();
        customer.setCustomerName(dto.getName());
        customer.setEmail(dto.getEmail());
        
        Customer saved = customerRepository.save(customer);
        return convertToDTO(saved);
    }
    
    public List<CustomerDTO> getAllCustomers() {
        return customerRepository.findAll().stream()
            .map(this::convertToDTO)
            .collect(Collectors.toList());
    }
}
```

**Frappe (Controller/API):**
```python
# In customer.py (DocType controller)
class Customer(Document):
    # Business logic methods here
    def before_save(self):
        self.update_credit_limit()
    
    def calculate_lifetime_value(self):
        orders = frappe.get_all("Sales Order",
            filters={"customer": self.name},
            fields=["grand_total"]
        )
        return sum([o.grand_total for o in orders])

# Or in api.py (for service-like functions)
import frappe

@frappe.whitelist()  # Makes it accessible via API
def create_customer(customer_name, email):
    doc = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": customer_name,
        "email": email
    })
    doc.insert()
    frappe.db.commit()
    return doc.as_dict()

@frappe.whitelist()
def get_all_customers():
    return frappe.get_all("Customer",
        fields=["name", "customer_name", "email"]
    )
```

### 4. REST Controllers

**Java Spring (REST Controller):**
```java
@RestController
@RequestMapping("/api/customers")
public class CustomerController {
    @Autowired
    private CustomerService customerService;
    
    @GetMapping
    public ResponseEntity<List<CustomerDTO>> getAllCustomers() {
        return ResponseEntity.ok(customerService.getAllCustomers());
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<CustomerDTO> getCustomer(@PathVariable Long id) {
        return ResponseEntity.ok(customerService.getCustomer(id));
    }
    
    @PostMapping
    public ResponseEntity<CustomerDTO> createCustomer(@RequestBody CustomerDTO dto) {
        return ResponseEntity.status(HttpStatus.CREATED)
            .body(customerService.createCustomer(dto));
    }
    
    @PutMapping("/{id}")
    public ResponseEntity<CustomerDTO> updateCustomer(
            @PathVariable Long id, @RequestBody CustomerDTO dto) {
        return ResponseEntity.ok(customerService.updateCustomer(id, dto));
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteCustomer(@PathVariable Long id) {
        customerService.deleteCustomer(id);
        return ResponseEntity.noContent().build();
    }
}
```

**Frappe (API Methods):**
```python
# In apps/ais/ais/ais/api.py
import frappe
from frappe import _

# Frappe automatically provides REST endpoints for all DocTypes:
# GET    /api/resource/Customer
# GET    /api/resource/Customer/{id}
# POST   /api/resource/Customer
# PUT    /api/resource/Customer/{id}
# DELETE /api/resource/Customer/{id}

# Custom endpoints:
@frappe.whitelist()
def get_customer_details(customer_id):
    """GET /api/method/ais.api.get_customer_details"""
    customer = frappe.get_doc("Customer", customer_id)
    orders = frappe.get_all("Sales Order",
        filters={"customer": customer_id},
        fields=["name", "grand_total", "status"]
    )
    
    return {
        "customer": customer.as_dict(),
        "orders": orders,
        "total_orders": len(orders)
    }

@frappe.whitelist()
def create_customer_with_validation(data):
    """POST /api/method/ais.api.create_customer_with_validation"""
    if not data.get("email"):
        frappe.throw(_("Email is required"))
    
    doc = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": data.get("customer_name"),
        "email": data.get("email")
    })
    doc.insert()
    frappe.db.commit()
    
    return {"message": "Customer created", "name": doc.name}

# Allow guest access (like permitAll())
@frappe.whitelist(allow_guest=True)
def public_endpoint():
    return {"message": "Public data"}
```

### 5. Dependency Injection

**Java Spring:**
```java
@Service
public class OrderService {
    @Autowired
    private CustomerRepository customerRepository;
    
    @Autowired
    private EmailService emailService;
    
    // Or constructor injection (preferred)
    public OrderService(CustomerRepository customerRepository, 
                       EmailService emailService) {
        this.customerRepository = customerRepository;
        this.emailService = emailService;
    }
}
```

**Frappe (Import-based):**
```python
# No DI container, just import what you need
import frappe
from ais.utils.email import send_email
from ais.utils.validators import validate_phone

class Order(Document):
    def validate(self):
        # Use imported functions
        validate_phone(self.phone)
    
    def on_submit(self):
        send_email(self.customer)
        
    def get_customer(self):
        # Direct database access
        return frappe.get_doc("Customer", self.customer)
```

### 6. Configuration

**Java Spring (application.properties):**
```properties
spring.datasource.url=jdbc:mysql://localhost:3306/mydb
spring.datasource.username=root
spring.datasource.password=secret

app.email.enabled=true
app.payment.gateway.key=pk_live_123

server.port=8080
```

**Frappe (Multiple configs):**
```python
# site_config.json (site-specific, like application-prod.properties)
{
    "db_host": "mariadb",
    "db_name": "_0a189b99783e3c71",
    "db_password": "secret",
    "developer_mode": 1,
    "mail_server": "smtp.gmail.com"
}

# hooks.py (app-wide configuration)
app_name = "ais"
app_title = "AIS"
app_version = "1.0.0"

# Boot session values (like @Value)
boot_session = "ais.boot.get_boot_data"

# Scheduled tasks
scheduler_events = {
    "daily": ["ais.tasks.daily_cleanup"],
    "hourly": ["ais.tasks.sync_data"]
}

# Access in code
import frappe
email_enabled = frappe.conf.get("email_enabled", True)
api_key = frappe.get_site_config().get("api_key")
```

### 7. Validation

**Java Spring:**
```java
public class CustomerDTO {
    @NotNull(message = "Name is required")
    @Size(min = 2, max = 100)
    private String name;
    
    @Email(message = "Invalid email")
    private String email;
    
    @Pattern(regexp = "^\\+?[1-9]\\d{1,14}$")
    private String phone;
}

@PostMapping
public ResponseEntity<?> create(@Valid @RequestBody CustomerDTO dto,
                               BindingResult result) {
    if (result.hasErrors()) {
        return ResponseEntity.badRequest().body(result.getAllErrors());
    }
    // ...
}
```

**Frappe:**
```python
# In DocType JSON definition
{
    "fields": [
        {
            "fieldname": "customer_name",
            "fieldtype": "Data",
            "reqd": 1,  # @NotNull
            "label": "Customer Name"
        },
        {
            "fieldname": "email",
            "fieldtype": "Data",
            "reqd": 1,
            "options": "Email"  # Built-in email validation
        }
    ]
}

# Custom validation in controller
class Customer(Document):
    def validate(self):
        self.validate_name()
        self.validate_phone()
        
    def validate_name(self):
        if len(self.customer_name) < 2:
            frappe.throw("Name must be at least 2 characters")
    
    def validate_phone(self):
        import re
        pattern = r'^\+?[1-9]\d{1,14}$'
        if self.phone and not re.match(pattern, self.phone):
            frappe.throw("Invalid phone number format")
```

### 8. Transactions

**Java Spring:**
```java
@Transactional
public void transferFunds(Long fromId, Long toId, BigDecimal amount) {
    Account from = accountRepository.findById(fromId)
        .orElseThrow(() -> new NotFoundException());
    Account to = accountRepository.findById(toId)
        .orElseThrow(() -> new NotFoundException());
    
    from.setBalance(from.getBalance().subtract(amount));
    to.setBalance(to.getBalance().add(amount));
    
    accountRepository.save(from);
    accountRepository.save(to);
}
```

**Frappe:**
```python
def transfer_funds(from_account, to_account, amount):
    # Automatic transaction handling
    from_doc = frappe.get_doc("Account", from_account)
    to_doc = frappe.get_doc("Account", to_account)
    
    from_doc.balance -= amount
    to_doc.balance += amount
    
    from_doc.save()
    to_doc.save()
    
    frappe.db.commit()  # Commit transaction
    
    # Or rollback on error
    try:
        # operations
        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()
        raise
```

### 9. Testing

**Java Spring (JUnit):**
```java
@SpringBootTest
@AutoConfigureMockMvc
public class CustomerControllerTest {
    @Autowired
    private MockMvc mockMvc;
    
    @MockBean
    private CustomerService customerService;
    
    @Test
    public void testGetAllCustomers() throws Exception {
        List<CustomerDTO> customers = Arrays.asList(
            new CustomerDTO("John", "john@example.com")
        );
        
        when(customerService.getAllCustomers()).thenReturn(customers);
        
        mockMvc.perform(get("/api/customers"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].name").value("John"));
    }
}
```

**Frappe (unittest):**
```python
# In tests/test_customer.py
import frappe
import unittest

class TestCustomer(unittest.TestCase):
    def setUp(self):
        # Create test data
        self.customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": "Test Customer",
            "email": "test@example.com"
        }).insert()
    
    def tearDown(self):
        # Clean up
        frappe.delete_doc("Customer", self.customer.name)
        frappe.db.commit()
    
    def test_customer_creation(self):
        self.assertEqual(self.customer.customer_name, "Test Customer")
        self.assertIsNotNone(self.customer.name)
    
    def test_email_validation(self):
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": "Invalid",
            "email": "invalid-email"
        })
        
        with self.assertRaises(frappe.ValidationError):
            customer.insert()

# Run tests
# bench --site ais.localhost run-tests --app ais
```

## 🛠️ Development Workflow Comparison

### Java Spring + Gradle
```bash
# Clone repository
git clone https://github.com/company/project.git
cd project

# Build
./gradlew build

# Run tests
./gradlew test

# Start application
./gradlew bootRun

# Hot reload (with DevTools)
# Automatic on file change
```

### Frappe + Bench
```bash
# Initialize bench
bench init --frappe-branch version-15 frappe-bench
cd frappe-bench

# Get app (like git clone + add dependency)
bench get-app https://github.com/company/ais.git

# Create site
bench new-site ais.localhost

# Install app on site
bench --site ais.localhost install-app ais

# Run tests
bench --site ais.localhost run-tests --app ais

# Start development server (with hot reload)
bench start

# Build assets
bench build --app ais
```

## 🔧 Best Practices: Maintain Java Discipline

### 1. **Project Organization**
```
apps/ais/ais/ais/
├── doctype/           # Like domain/entity
├── services/          # CREATE THIS - Service layer
│   ├── __init__.py
│   ├── customer_service.py
│   └── order_service.py
├── repositories/      # CREATE THIS - Data access
│   ├── __init__.py
│   └── customer_repository.py
├── api/               # CREATE THIS - Controllers
│   ├── __init__.py
│   ├── customer_api.py
│   └── order_api.py
├── validators/        # CREATE THIS - Validation logic
│   ├── __init__.py
│   └── email_validator.py
├── dto/              # CREATE THIS - Data transfer objects
│   ├── __init__.py
│   └── customer_dto.py
└── utils/            # Utility classes
```

### 2. **Separation of Concerns (Spring-like)**

```python
# repositories/customer_repository.py
class CustomerRepository:
    @staticmethod
    def find_by_email(email):
        return frappe.db.get_value("Customer", {"email": email}, "*", as_dict=True)
    
    @staticmethod
    def find_all():
        return frappe.get_all("Customer", fields=["*"])
    
    @staticmethod
    def save(customer_dict):
        doc = frappe.get_doc(customer_dict)
        doc.save()
        return doc

# services/customer_service.py
from ais.repositories.customer_repository import CustomerRepository
from ais.validators.email_validator import EmailValidator

class CustomerService:
    def __init__(self):
        self.repository = CustomerRepository()
        self.validator = EmailValidator()
    
    def create_customer(self, customer_data):
        # Validate
        if not self.validator.is_valid(customer_data.get("email")):
            frappe.throw("Invalid email")
        
        # Business logic
        customer_data["doctype"] = "Customer"
        
        # Save
        return self.repository.save(customer_data)
    
    def get_customer_by_email(self, email):
        return self.repository.find_by_email(email)

# api/customer_api.py
import frappe
from ais.services.customer_service import CustomerService

@frappe.whitelist()
def create_customer(customer_name, email):
    service = CustomerService()
    return service.create_customer({
        "customer_name": customer_name,
        "email": email
    })

@frappe.whitelist()
def get_customer(email):
    service = CustomerService()
    return service.get_customer_by_email(email)
```

### 3. **Use Type Hints (Like Java Types)**

```python
from typing import List, Optional, Dict
import frappe

def get_customers(status: str) -> List[Dict]:
    return frappe.get_all("Customer",
        filters={"status": status},
        fields=["name", "email"]
    )

def find_customer(customer_id: str) -> Optional[Dict]:
    if frappe.db.exists("Customer", customer_id):
        return frappe.get_doc("Customer", customer_id).as_dict()
    return None

class CustomerService:
    def calculate_total(self, amounts: List[float]) -> float:
        return sum(amounts)
```

### 4. **DTO Pattern**

```python
# dto/customer_dto.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class CustomerDTO:
    customer_name: str
    email: str
    phone: Optional[str] = None
    status: str = "Active"
    
    def to_dict(self) -> dict:
        return {
            "doctype": "Customer",
            "customer_name": self.customer_name,
            "email": self.email,
            "phone": self.phone,
            "status": self.status
        }
    
    @staticmethod
    def from_doc(doc) -> 'CustomerDTO':
        return CustomerDTO(
            customer_name=doc.customer_name,
            email=doc.email,
            phone=doc.phone,
            status=doc.status
        )

# Usage
from ais.dto.customer_dto import CustomerDTO

dto = CustomerDTO(
    customer_name="John Doe",
    email="john@example.com"
)
customer = frappe.get_doc(dto.to_dict())
customer.insert()
```

### 5. **Dependency Management**

```python
# requirements.txt (like build.gradle dependencies)
frappe>=15.0.0
pandas==2.0.0
requests==2.32.5
python-dateutil>=2.8.0

# Install: bench pip install -r requirements.txt
# Or in pyproject.toml (like Gradle with version catalog)
```

### 6. **Exception Handling**

```java
// Java
@ControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(NotFoundException.class)
    public ResponseEntity<?> handleNotFound(NotFoundException ex) {
        return ResponseEntity.status(404).body(ex.getMessage());
    }
}
```

```python
# Frappe
import frappe

class NotFoundException(frappe.ValidationError):
    pass

def get_customer(customer_id):
    if not frappe.db.exists("Customer", customer_id):
        frappe.throw("Customer not found", NotFoundException)
    
    return frappe.get_doc("Customer", customer_id)

# Or use try-catch
try:
    customer = frappe.get_doc("Customer", "INVALID")
except frappe.DoesNotExistError:
    frappe.throw("Customer not found", exc=NotFoundException)
```

## 📊 IDE Setup

### Java (IntelliJ IDEA)
- Spring Initializr
- Gradle integration
- Auto-completion
- Debugging

### Python/Frappe (VS Code - Recommended)
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "/workspace/development/frappe-bench/env/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter",
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    }
}
```

## 🚀 Quick Reference

| Task | Java/Gradle | Frappe/Bench |
|------|------------|--------------|
| Build | `./gradlew build` | `bench build` |
| Run | `./gradlew bootRun` | `bench start` |
| Test | `./gradlew test` | `bench run-tests` |
| Clean | `./gradlew clean` | `bench clear-cache` |
| Dependency | add to build.gradle | add to requirements.txt |
| Database migration | Liquibase/Flyway | `bench migrate` |
| Hot reload | Spring DevTools | Auto (developer mode) |

## 💡 Key Mindset Shifts

1. **No compile step** - Python is interpreted
2. **Convention over configuration** - Less boilerplate
3. **Duck typing** - No strict interfaces (but use type hints!)
4. **DocTypes are entities** - Schema + Controller in one
5. **Built-in ORM** - No need for JPA/Hibernate
6. **Automatic API** - Every DocType gets REST endpoints
7. **Framework magic** - More convention, less explicit config

## 🎓 Learning Path

1. ✅ Understand Frappe concepts (you're here!)
2. Build a simple CRUD DocType
3. Add custom API endpoints
4. Implement business logic in controllers
5. Write tests
6. Create reports and dashboards
7. Advanced: Workflows, permissions, integrations

You can absolutely maintain Java's structured approach in Frappe - create service layers, repositories, DTOs, and follow SOLID principles!
