# models.py (More Flexible Version)
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date

class Receipt(BaseModel):
    """
    Pydantic model for validating parsed receipt data.
    Fields are now optional to handle cases where the AI fails to extract a value.
    """
    vendor: Optional[str] = None
    transaction_date: Optional[date] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    raw_text: str
    currency: Optional[str] = "USD"

    @field_validator('amount')
    @classmethod
    def amount_must_be_positive(cls, v: Optional[float]) -> Optional[float]:
        """Validator to ensure the amount is positive, if it exists."""
        if v is not None and v <= 0:
            raise ValueError('Amount must be positive')
        return v