from dataclasses import dataclass
from typing import Any
from decimal import Decimal, InvalidOperation
from datetime import date as Date

# defines what an expense includes
@dataclass
class Expense:
    id: int
    title: str
    amount: Decimal
    date: Date
    category: str
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "amount": format(self.amount, ".2f"), # consistent format e.g. 12.5 -> 12.50
            "date": self.date.isoformat(),
            "category": self.category,
            "description": self.description,
        }

class ValidationError(ValueError):
    """Raised when client input does not satisfy the Task invariants."""


# validation functions ensure consitent and correct data
# functions are used in repository.py when creating or updating an expense

# validate_title function copied from beispiel-app/models.py
# other validation functinons are adapted to the requirements of the expenses management application

def validate_title(raw: Any) -> str:
    if not isinstance(raw, str):
        raise ValidationError("Title must be a string.")
    title = raw.strip()
    if not title:
        raise ValidationError("Title cannot be empty.")
    if len(title) > 200:
        raise ValidationError("Title cannot exceed 200 characters.")
    return title

def validate_amount(raw: Any) -> Decimal:
    if not isinstance(raw, str):
        raise ValidationError('Amount must be a decimal string, e.g. "18.55".')  
    try:
        amount = Decimal(raw)
    except InvalidOperation:
        raise ValidationError("Amount must be a valid decimal number.") from None
    if not amount.is_finite():
        raise ValidationError("Amount must be finite.")
    if amount <= 0:
        raise ValidationError("Amount must be greater than zero.")
    # max. of decimal places
    if amount.as_tuple().exponent < -2:
        raise ValidationError("Amount must have at most two decimal places.")
    return amount

def validate_date(raw: Any) -> Date:
    if not isinstance(raw, str):
        raise ValidationError("Date must be a string in YYYY-MM-DD format.")
    try: 
        parsed = Date.fromisoformat(raw)
    except ValueError:
        raise ValidationError("Date must be a valid date in YYYY-MM-DD format.") from None
    if parsed.isoformat() != raw:
        raise ValidationError("Date must be in YYYY-MM-DD format.")
    return parsed

def validate_description(raw: Any) -> str:
    if raw is None:
        return "" # description is optional
    if not isinstance(raw, str):
        raise ValidationError("Description must be a string.")
    return raw

category_list = [
    "Food",
    "Transport",
    "Home",
    "Entertainment",
    "Shopping",
    "Health",
    "Insurance",
    "Education",
    "Travel",
    "Subscriptions",
    "Savings",
    "Car",
    "Other"
    ]

def validate_category(raw: Any) -> str:
    if not isinstance(raw, str):
        raise ValidationError("Category must be a string.")
    category = raw.strip()
    if not category:
        raise ValidationError("Category cannot be empty.")
    if not category in category_list:
        raise ValidationError(f"Category must be one of {category_list}.")
    return category

# maybe in future:
# def validate_currency(raw: Any) -> str:
# def validate_payment_method(raw: Any) -> str:
# def validate_recurring(raw: Any) -> bool:
