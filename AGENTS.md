# AGENTS.md - CvSU AIS Implementation Instructions (Frappe/ERPNext)

## Scope
These instructions apply to this workspace for building the CvSU Accounting Information System (AIS) in Frappe/ERPNext.

## Fixed Architecture Decisions
- Use `hybrid` design:
  - Charter control workflows are custom Frappe DocTypes and Workflows.
  - ERPNext Accounting is the ledger source of truth (`Journal Entry`, `Payment Entry`, `GL Entry`).
- Use `Pattern A` identity:
  - Authentication via Google SSO.
  - Authorization via AD group to Frappe role mapping (sync on login and scheduled sync).
- Use `one site` deployment for all modules.
- Enforce strict Segregation of Duties (SoD) and least privilege.

## Core Process Coverage (MVP)
- Disbursement (DV lifecycle, control numbering, posting, release status)
- Collections (Cashier intake, Official Receipt issuance, posting)
- Internal Audit (Received -> Recorded -> Audited -> Released)
- COA Disallowance/Charge Monitoring (ND/NC -> NFD -> COE -> settlement)
- ORS/BURS registry and linkage validation
- Audit trail and attachment evidence management

## DocType Strategy
- Keep Charter control documents as custom DocTypes (AIS domain docs).
- Post financial impact to ERPNext accounting docs; never bypass ERPNext posting flow.
- Required control documents:
  - `AIS ORS/BURS`
  - `AIS Disbursement Voucher`
  - `AIS Official Receipt` (or controlled wrapper around Payment Entry + OR print/registry)
  - `AIS Audit Intake`
  - `AIS COA Case` (+ ND/NC, NFD, COE, Settlement child records)

## Hard Rules (Must Enforce in Code)
- Fund cluster isolation: never mix fund clusters in queries or postings.
- No-budget lock on DV: block submit/approval when linked ORS/BURS balance is insufficient.
- Required attachments by transaction type before submit.
- SoD blocking:
  - Preparer/Encoder cannot be Approver/Releaser of the same transaction.
  - Cashier OR issuer cannot approve disbursements.
  - IA cannot originate the same DV it audits.
- UACS validation: referenced UACS/account must exist and be valid before submit/post.
- Precision handling: use `frappe.utils.flt` with controlled precision (display 2, internal up to 4).

## Posting Policy
- DV final approval -> create ERPNext `Journal Entry` and/or `Payment Entry` as configured.
- OR issuance -> create ERPNext `Payment Entry` (or approved AR flow when required).
- COA settlement:
  - Direct payment -> posting via `Payment Entry`.
  - Payroll deduction remittance -> periodic settlement posting with OR/remittance evidence.
- Store posting references and timestamps back in AIS control documents.

## Security and Access
- Role assignment should come from AD group mapping; avoid manual role grants.
- If exception access is needed, implement time-bound temporary grants with approval reference and auto-revoke scheduler.
- Restrict data by campus/cost center using User Permissions.

## Implementation Standards
- Put core business rules in app Python code/hooks (`validate`, `before_submit`, `on_submit`).
- Keep client scripts for UX help only; do not rely on them for critical enforcement.
- Do not directly edit ERPNext core behavior unless unavoidable; prefer extension/customization patterns.
- Keep changes idempotent, testable, and migration-safe.

## Minimum Test Coverage
- SoD conflict enforcement
- Required attachment enforcement
- Control number uniqueness and sequence integrity
- Fund cluster isolation in fetch/post flows
- Permission boundaries by role and by user permission
- Posting link integrity (control doc -> accounting doc)

## Definition of Done
- DocType model + workflow implemented
- Permissions and SoD controls enforced
- Audit trail and attachments verifiable
- Required operational reports available (OR register, DV aging/status, COA case aging, IA throughput)
- Automated tests pass

