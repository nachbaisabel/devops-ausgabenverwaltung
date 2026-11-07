from flask import Blueprint, current_app, jsonify, request

from app.models import (
    ValidationError,
    validate_amount,
    validate_category,
    validate_date,
    validate_description,
    validate_title,
)

bp = Blueprint("main", __name__)


@bp.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify(error=str(error)), 400


# Helper function to access the repository from the current app context
def _repo():
    return current_app.extensions["repository"]


# simple health check endpoint to verify that the application is running
# copied from beispiel-app/routes.py
@bp.get("/health")
def health():
    """
    Liveness: is the process up? Must not touch the database.

    Kubernetes restarts the container when this fails, so a slow database
    must never be able to trigger a restart loop.
    """
    return jsonify(status="ok")


# endpoint to get expenses
@bp.get("/api/expenses")
def get_expenses():
    return jsonify([t.to_dict() for t in _repo().list()])


# endpoint to post expenses
@bp.post("/api/expenses")
def create_expenses():
    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        raise ValidationError("Request body must be a JSON object.")

    # validate-functions from models.py
    title = validate_title(payload.get("title"))
    amount = validate_amount(payload.get("amount"))
    date = validate_date(payload.get("date"))
    category = validate_category(payload.get("category"))
    description = validate_description(payload.get("description"))

    expense = _repo().add(title, amount, date, category, description)

    return jsonify(expense.to_dict()), 201


# endpoint to modify expenses
@bp.put("/api/expenses/<int:expense_id>")
def update_expense(expense_id):
    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        raise ValidationError("Request body must be a JSON object.")

    # validate-functions from models.py
    title = validate_title(payload.get("title"))
    amount = validate_amount(payload.get("amount"))
    date = validate_date(payload.get("date"))
    category = validate_category(payload.get("category"))
    description = validate_description(payload.get("description"))

    expense = _repo().update(expense_id, title, amount, date, category, description)

    if expense is None:
        return jsonify({"error": "Expense not found"}), 404

    return jsonify(expense.to_dict()), 200


# endpoint to delete expenses
@bp.delete("/api/expenses/<int:expense_id>")
def delete_expense(expense_id):
    success = _repo().delete(expense_id)

    if not success:
        return jsonify({"error": "Expense not found"}), 404

    return jsonify({"message": "Expense deleted successfully"}), 200


# future endpoints to implement:
# - endpoint to calculate expenses by category
# - endpoint to calculate expensesby by month

# - endpoint to get all expenses by title search
# - endpoint to calculate expenses by amount range
