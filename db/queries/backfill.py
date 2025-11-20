#  J. Backfill / Reconciliation

# Endpoints to reconcile missed events while offline.

# POST /backfill/channel/{channel_id} – Fetch older messages for backfill.

# POST /reconcile/channel/{channel_id} – Fetch messages/edits/deletions since last sync.

# POST /reconcile/all – Periodic reconciliation for all channels.