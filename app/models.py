from dataclasses import dataclass
from typing import Any

# defines what an expense includes
@dataclass
class Expense:
    id: int
    title: str
    amount: float
    date: str # YYYY-MM-DD
    category: str
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "amount": self.amount,
            "date": self.date,
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

def validate_amount(raw: Any) -> float:
    if not isinstance(raw, (int, float)):
        raise ValidationError("Amount must be a number.")
    amount = float(raw)
    if not amount > 0:
        raise ValidationError("Amount must be greater than zero.")
    return amount

def validate_date(raw: Any) -> str:
    if not isinstance(raw, str):
        raise ValidationError("Date must be a string in YYYY-MM-DD format.")
    # Basic validation for date format (YYYY-MM-DD)
    parts = raw.split("-")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise ValidationError("Date must be in YYYY-MM-DD format.")
    year, month, day = map(int, parts)
    if not (1 <= month <= 12 and 1 <= day <= 31):
        raise ValidationError("Invalid month or day in date.")
    return raw

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
