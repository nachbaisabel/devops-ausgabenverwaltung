# from __future__ import annotations

import logging
import threading
# from typing import Protocol

# from app.config import Config
from app.models import Expense


# ! structure of file is inspired by beispiel-app/repository.py

log = logging.getLogger(__name__)


# class ExpenseRepository(Protocol):


class InMemoryExpenseRepository:
    """
    Default backend. Data is lost when the process exits.
    Good enough for tests and for week 3, where no database exists yet.
    """

    # define methods for repository class, which will be used in routes.py to access the data
    def __init__(self) -> None:
        self._expenses: dict[int, Expense] = {}
        self._next_id = 1 # next id to assign to a new expense
        self._lock = threading.Lock() # lock if multiple threads access the repository concurrently

    def list(self) -> list[Expense]:
        with self._lock:
            return list(self._expenses.values())

    def get(self, expense_id: int) -> Expense | None:
        with self._lock:
            return self._expenses.get(expense_id)

    def add(self, title: str, amount: float, date: str, category: str, description: str = "") -> Expense:
        with self._lock:
            expense = Expense(
                id=self._next_id,
                title=title,
                amount=amount,
                date=date,
                category=category,
                description=description
            )
            self._expenses[self._next_id] = expense
            self._next_id += 1
            return expense

    def update(self, expense_id: int, title: str, amount: float, date: str, category: str, description: str = "") -> Expense | None:
        with self._lock:
            if expense_id not in self._expenses:
                return None
            expense = Expense(
                id=expense_id,
                title=title,
                amount=amount,
                date=date,
                category=category,
                description=description
            )
            self._expenses[expense_id] = expense
            return expense

    def delete(self, expense_id: int) -> bool:
        with self._lock:
            return self._expenses.pop(expense_id, None) is not None

    def healthy(self) -> bool:
        return True


#class PostgresExpenseRepository:
    """Postgres backend, used from week 4 onwards via Docker Compose."""



# def create_repository(config: Config) -> ExpenseRepository:
