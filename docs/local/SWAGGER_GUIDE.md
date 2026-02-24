# Swagger/OpenAPI Documentation for Frappe

## Quick Answer

**Yes!** You can generate Swagger documentation for your Frappe apps. There are two approaches:

1. **Community App** - Use the `frappe-openapi` app
2. **Custom Implementation** - Create your own (I've created one for you)

---

## Method 1: Using frappe-openapi App (Easiest)

### Installation

```bash
# Inside the frappe container
docker compose -f .devcontainer/docker-compose.yml exec frappe bash

cd /workspace/development/frappe-bench

# Get the app
bench get-app https://github.com/frappe/openapi

# Install on your site
bench --site ais.localhost install-app openapi

# Restart
bench restart
```

### Access Swagger UI

Visit: `http://ais.localhost:8000/openapi`

This will show:
- All DocType CRUD endpoints
- Custom @frappe.whitelist() methods
- Request/response schemas
- Try it out feature (like Swagger UI in Spring)

---

## Method 2: Custom Swagger Generator (Full Control)

I've created a custom Swagger generator at:
```
apps/ais/ais/ais/api/swagger.py
```

### How to Use

1. **View Swagger UI:**
   ```
   http://ais.localhost:8000/api/method/ais.api.swagger.get_swagger_ui
   ```

2. **Get OpenAPI JSON:**
   ```
   http://ais.localhost:8000/api/method/ais.api.swagger.get_openapi_spec
   ```

3. **Import to Postman/Insomnia:**
   - Export the JSON spec
   - Import into your API client

### Features

✅ Auto-generates endpoints for all DocTypes  
✅ Documents custom @frappe.whitelist() methods  
✅ Includes authentication schemas  
✅ Swagger UI interface  
✅ Full OpenAPI 3.0 compliance  

---

## Built-in Frappe API Explorer

Frappe also has a built-in API explorer (without Swagger UI):

### Access:
```
http://ais.localhost:8000/api
```

### View Available Resources:
```bash
# Inside frappe container
bench --site ais.localhost console

# In console:
>>> import frappe
>>> frappe.get_all("DocType", fields=["name"])
```

---

## Comparison with Java Spring

| Java Spring Boot | Frappe Framework |
|-----------------|------------------|
| SpringDoc/Springfox | frappe-openapi or custom |
| `@Operation` annotations | Auto-generated from DocTypes |
| `@ApiModel` | DocType schema |
| `/swagger-ui.html` | `/openapi` or custom route |
| `@Tag` | DocType name or custom tags |

---

## Example: Document Custom API

### Java Spring (with Swagger)
```java
@RestController
@Tag(name = "Customer", description = "Customer management APIs")
public class CustomerController {
    
    @Operation(summary = "Get customer by ID")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Found customer"),
        @ApiResponse(responseCode = "404", description = "Customer not found")
    })
    @GetMapping("/api/customers/{id}")
    public ResponseEntity<CustomerDTO> getCustomer(@PathVariable Long id) {
        // ...
    }
}
```

### Frappe (with custom Swagger)
```python
import frappe

@frappe.whitelist()
def get_customer(customer_id):
    """
    Get customer by ID
    
    Args:
        customer_id (str): Customer ID
    
    Returns:
        dict: Customer details
        
    Raises:
        frappe.DoesNotExistError: Customer not found
    """
    return frappe.get_doc("Customer", customer_id).as_dict()

# Add to swagger.py's get_custom_endpoints():
paths["/api/method/ais.api.get_customer"] = {
    "get": {
        "summary": "Get customer by ID",
        "tags": ["Customer"],
        "parameters": [{
            "name": "customer_id",
            "in": "query",
            "required": True,
            "schema": {"type": "string"}
        }],
        "responses": {
            "200": {"description": "Customer found"},
            "404": {"description": "Customer not found"}
        }
    }
}
```

---

## Automatic REST API Endpoints

Every DocType automatically gets these endpoints (no code needed):

```bash
# List all records
GET /api/resource/Customer?fields=["name","email"]&filters=[["status","=","Active"]]

# Get single record
GET /api/resource/Customer/CUST-001

# Create record
POST /api/resource/Customer
Body: {"customer_name": "John", "email": "john@example.com"}

# Update record
PUT /api/resource/Customer/CUST-001
Body: {"phone": "123-456-7890"}

# Delete record
DELETE /api/resource/Customer/CUST-001
```

These are all documented in Swagger!

---

## Testing APIs (Like Postman in Spring)

### 1. **Frappe REST Client (Built-in)**
```bash
# Inside frappe container
bench --site ais.localhost console

>>> import frappe
>>> frappe.get_all("Customer", filters={"status": "Active"})
```

### 2. **Swagger UI "Try it out"**
- Visit Swagger UI
- Click endpoint
- Click "Try it out"
- Fill parameters
- Execute

### 3. **cURL Examples**
```bash
# Get with API key
curl -X GET "http://ais.localhost:8000/api/resource/Customer" \
  -H "Authorization: token <api_key>:<api_secret>"

# Create
curl -X POST "http://ais.localhost:8000/api/resource/Customer" \
  -H "Content-Type: application/json" \
  -H "Authorization: token <api_key>:<api_secret>" \
  -d '{"customer_name": "Test", "email": "test@example.com"}'
```

### 4. **Generate API Keys**
```python
# In bench console or via UI
user = "administrator"
frappe.get_doc({
    "doctype": "API Secret",
    "user": user
}).insert()
```

Or via UI: Settings → API Access → Generate Keys

---

## Advanced: Auto-generate from Docstring

You can use Python docstrings to auto-generate API docs:

```python
import frappe
from typing import List, Dict

@frappe.whitelist()
def search_customers(query: str, limit: int = 20) -> List[Dict]:
    """
    Search customers by name or email
    
    This endpoint searches across customer names and emails.
    
    Args:
        query: Search term
        limit: Maximum results (default: 20)
    
    Returns:
        List of matching customers
        
    Example:
        >>> search_customers("john", 10)
        [{"name": "CUST-001", "customer_name": "John Doe"}]
    """
    return frappe.db.sql("""
        SELECT name, customer_name, email 
        FROM `tabCustomer`
        WHERE customer_name LIKE %(query)s 
           OR email LIKE %(query)s
        LIMIT %(limit)s
    """, {"query": f"%{query}%", "limit": limit}, as_dict=True)
```

Then parse these docstrings in your Swagger generator!

---

## Next Steps

1. **Install frappe-openapi** for quick setup
2. **Or use custom swagger.py** for full control
3. **Document your custom APIs** in the get_custom_endpoints() function
4. **Generate API keys** for testing
5. **Share Swagger URL** with frontend developers

The Swagger documentation will be just like Spring Boot's SpringDoc! 🎯
