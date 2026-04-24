"""
models.py — Expense Tracker data layer

Key decisions:
  - DecimalField for amount: avoids float rounding errors (e.g. 0.1 + 0.2 ≠ 0.3 in IEEE 754).
    We store up to 10 digits total with 2 decimal places (max ₹99,999,999.99).
  - date field is DateField (not DateTimeField): the user records *when* the expense occurred,
    not the exact second. This matches real-world expense tracking (receipts show dates, not times).
  - created_at uses auto_now_add so it is set once on insert and never changes.
  - IdempotencyKey stores the client-generated UUID keyed to an Expense so that retried
    POST requests return the already-created expense rather than creating a duplicate.
    The key expires after IDEMPOTENCY_TTL_HOURS so the table does not grow forever.
"""

import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone


class Category(models.TextChoices):
    """
    Fixed category list keeps the data clean and enables reliable filtering.
    'OTHER' is the escape hatch for anything that doesn't fit.
    Adding new categories is a migration + code change — intentional friction
    to prevent category proliferation.
    """
    FOOD = "food", "Food & Dining"
    TRANSPORT = "transport", "Transport"
    UTILITIES = "utilities", "Utilities"
    ENTERTAINMENT = "entertainment", "Entertainment"
    HEALTH = "health", "Health & Medical"
    SHOPPING = "shopping", "Shopping"
    EDUCATION = "education", "Education"
    RENT = "rent", "Rent & Housing"
    OTHER = "other", "Other"


class Expense(models.Model):
    """
    Core expense record.

    amount  — stored as DECIMAL(10, 2), validated ≥ 0.01 at the serializer layer.
    date    — the calendar date of the expense (not the creation timestamp).
    created_at — immutable server timestamp; used for tie-breaking sorts.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=Category.choices)
    description = models.CharField(max_length=500, blank=False)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]  # default: newest first
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["-date", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.date} | {self.category} | ₹{self.amount} | {self.description[:40]}"


# ── Idempotency ────────────────────────────────────────────────────────────────

IDEMPOTENCY_TTL_HOURS = 24


class IdempotencyKey(models.Model):
    """
    Maps a client-generated UUID to the Expense it created.

    When a client retries a POST (network blip, double-click, page reload),
    it sends the same idempotency_key. The view looks up the key and returns
    the existing Expense instead of inserting a duplicate.

    Records older than IDEMPOTENCY_TTL_HOURS are safe to delete (via a
    management command or cron job in production).
    """

    key = models.UUIDField(primary_key=True)
    expense = models.OneToOneField(
        Expense,
        on_delete=models.CASCADE,
        related_name="idempotency_key",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),  # for TTL cleanup queries
        ]

    @classmethod
    def is_expired(cls, record):
        return timezone.now() - record.created_at > timedelta(hours=IDEMPOTENCY_TTL_HOURS)

    def __str__(self):
        return f"IdempotencyKey({self.key}) → Expense({self.expense_id})"