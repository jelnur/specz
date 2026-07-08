---
id: spz-sec-k9
type: non-functional
status: todo
---
# Account lockout policy

## Description
Brute-force protection for authentication endpoints; enforced by the login
flow ([[spz-auth-bz]]).

## Acceptance Criteria
- [ ] 5 consecutive failures locks the account
- [ ] a lock expires after 15 minutes
