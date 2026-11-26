# Deploy pipeline

Merges to main trigger staging. Production deploy needs a green pipeline and an approved change ticket.
Rollback uses the previous container image tag. Hotfixes still go through CI.
