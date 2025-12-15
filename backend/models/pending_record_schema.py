#backend/models/pending_record_schema.py
# UTF-8, English only

from pydantic import BaseModel


class ApproveRecordRequest(BaseModel):
    """
    Schema for approving a pending record.
    This is the payload received by the /approve endpoint.
    """
    pending_id: str
