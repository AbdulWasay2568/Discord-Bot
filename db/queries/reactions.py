from sqlalchemy.orm import Session

# E. Reactions

# Endpoints to track message reactions.

# POST /messages/{message_id}/reactions – Add a reaction.

# DELETE /messages/{message_id}/reactions – Remove a reaction.

# GET /messages/{message_id}/reactions – List reactions with counts.