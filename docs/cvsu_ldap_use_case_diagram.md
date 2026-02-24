# CvSU LDAP Integration Use Case Diagram

This diagram shows AD/LDAP authentication at Frappe core and authorization via LDAP group to Frappe role mapping for `cvsu_hris`, `accounting`, and `payments`.

```mermaid
flowchart LR
    User["CvSU User"]
    ITAdmin["IT / Identity Admin"]
    ModuleAdmin["Module Admin<br/>(HR / Accounting / Payments)"]

    AD["Active Directory"]
    Groups["AD Security Groups\n(CVSU-ERP-*)"]

    FrappeLogin["Frappe Login\nLDAP Settings Enabled"]
    LDAPBind["LDAP Bind + User Search\n(sAMAccountName)"]
    Provision["Create/Update Frappe User"]
    RoleSync["Sync Roles from LDAP Group Mappings"]

    HRIS["CvSU HRIS"]
    Accounting["Accounting"]
    Payments["Payments"]

    SoD["SoD Control\n(Encoder != Approver)"]
    Audit["Audit Trail\n(Login + Role Changes)"]

    User -->|"Login"| FrappeLogin
    FrappeLogin --> LDAPBind
    LDAPBind --> AD
    AD --> Groups
    Groups --> RoleSync
    LDAPBind --> Provision
    Provision --> RoleSync

    RoleSync --> HRIS
    RoleSync --> Accounting
    RoleSync --> Payments

    ITAdmin -->|"Maintain AD users/groups"| AD
    ModuleAdmin -->|"Define role mappings in LDAP Settings"| RoleSync

    Accounting --> SoD
    RoleSync --> Audit

    classDef core fill:#f5f8ff,stroke:#3b5bdb,stroke-width:1px;
    classDef ext fill:#eefaf1,stroke:#2b8a3e,stroke-width:1px;
    classDef ctrl fill:#fff5f5,stroke:#c92a2a,stroke-width:1px;

    class FrappeLogin,LDAPBind,Provision,RoleSync core;
    class AD,Groups ext;
    class SoD,Audit ctrl;
```

## Role Mapping Reference (Pilot)

- `CVSU-ERP-HRIS-EMPLOYEE` -> `Employee`
- `CVSU-ERP-HRIS-OFFICER` -> `HR User`
- `CVSU-ERP-HRIS-MANAGER` -> `HR Manager`
- `CVSU-ERP-ACCT-ENCODER` -> `Accounts User`
- `CVSU-ERP-ACCT-APPROVER` -> `Accounts Manager`
- `CVSU-ERP-PAYMENTS-ADMIN` -> `System Manager`

## Primary Use Cases

1. User logs in once via AD credentials and gains app access based on mapped roles.
2. Onboarding/offboarding happens by adding/removing AD group membership.
3. Accounting segregation of duties is enforced through distinct AD groups.
4. Payment operations remain role-gated and auditable via centralized identity.
