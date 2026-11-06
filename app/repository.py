from decimal import Decimal 
from datetime import date as Date
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

    def add(self, title: str, amount: Decimal, date: Date, category: str, description: str = "") -> Expense:
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

    def update(self, expense_id: int, title: str, amount: Decimal, date: Date, category: str, description: str = "") -> Expense | None:
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


class PostgresExpenseRepository:
    """Postgres backend, used from week 4 onwards via Docker Compose."""

    # provides database connections
    def __init__(self, dsn: str) -> None:
        import psycopg
        from psycopg_pool import ConnectionPool

        self._psycopg = psycopg
        self._pool = ConnectionPool(dsn, min_size=1, max_size=5, open=True)
        self._create_schema()

    # to create SQL-table expenses
    def _create_schema(self) -> None:
        with self._pool.connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    id    SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    amount NUMERIC(12,2) NOT NULL, -- money with two decimal places
                    date DATE NOT NULL,
                    category  TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT ''
                )
                """
            )

    # to read saved expenses out of the table
    def list(self) -> list[Expense]:
        with self._pool.connection() as conn:
            rows = conn.execute("SELECT id, title, amount, date, category, description FROM expenses ORDER BY id").fetchall()
        return [Expense(*row) for row in rows]

    # to add a expense to the table
    def add(self, title: str, amount: Decimal, date: Date, category: str, description: str = "") -> Expense:
        with self._pool.connection() as conn:
            row = conn.execute(
                "INSERT INTO expenses (title, amount, date, category, description) "
                "VALUES (%s, %s, %s, %s, %s) "
                "RETURNING id, title, amount, date, category, description",
                (title, amount, date, category, description),
            ).fetchone()
        return Expense(*row)

    # to get a expense by id from the table
    def get(self, expense_id: int) -> Expense | None:
        with self._pool.connection() as conn:
            row = conn.execute(
                "SELECT id, title, amount, date, category, description "
                "FROM expenses "
                "WHERE id = %s", (expense_id,)
            ).fetchone()
        return Expense(*row) if row else None

    # to update a expense by id in the table
    def update(self, expense_id: int, title: str, amount: Decimal, date: Date, category: str, description: str = "") -> Expense | None:
        with self._pool.connection() as conn:
            row = conn.execute(
                "UPDATE expenses "
                "SET title = %s, amount = %s, date = %s, category = %s, description = %s "
                "WHERE id = %s "
                "RETURNING id, title, amount, date, category, description",
                (title, amount, date, category, description, expense_id),
            ).fetchone()
        return Expense(*row) if row else None
    
    # to delete a expense by id in the table
    def delete(self, expense_id: int) -> bool:
        with self._pool.connection() as conn:
            result = conn.execute(
                "DELETE FROM expenses "
                "WHERE id = %s", 
                (expense_id,))
        return result.rowcount > 0

    # to check if the database is available
    def healthy(self) -> bool:
        try:
            with self._pool.connection() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception:
            log.exception("database health check failed")
            return False

    
                



# def create_repository(config: Config) -> ExpenseRepository:
