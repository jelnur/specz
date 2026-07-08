---
id: spz-auth-bz
type: functional
status: done
synced: 7a793e73
---
# Login with email+password

## Description
Users authenticate with email and password. Repeated failures trigger the
lockout policy defined in [[spz-sec-k9]].

## Acceptance Criteria
- [x] valid credentials → session issued
- [x] 5 consecutive failures → account locked for 15 minutes
- [x] a successful login resets the failure counter
