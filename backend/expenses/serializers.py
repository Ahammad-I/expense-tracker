"""
serializers.py — input validation and output shaping

Validation rules (all produce 400 with clear messages):
  - amount   : required, must be a valid decimal, must be ≥ 0.01, max 2 decimal places,
               max value 99999999.99 (fits DECIMAL(10,2))
  - category : required, must be one of the defined Category choices
  - description : required, non-blank, stripped of leading/trailing whitespace
  - date     : required, valid ISO-8601 date (YYYY-MM-DD), not in the far future (> 1 year)
  - idempotency_key (POST only): optional UUID; if absent a new one is generated server-side
"""

import uuid
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from rest_framework import serializers

from .models import Category, Expense


class ExpenseSerializer(serializers.ModelSerializer):
    # Return human-readable category label alongside the key
    category_display = serializers.CharField(source="get_category_display", read_only=True)

    # Expose idempotency_key so the client can confirm which key was used
    idempotency_key = serializers.SerializerMethodField()

    def get_idempotency_key(self, obj):
        try:
            return str(obj.idempotency_key.key)
        except Exception:
            return None

    class Meta:
        model = Expense
        fields = [
            "id",
            "amount",
            "category",
            "category_display",
            "description",
            "date",
            "created_at",
            "idempotency_key",
        ]
        read_only_fields = ["id", "created_at", "category_display"]

    # ── Field-level validation ─────────────────────────────────────────────────

    def validate_amount(self, value):
        """
        Reject amounts that are zero, negative, have more than 2 decimal places,
        or exceed the column's storage capacity.
        """
        # value arrives as Decimal (DRF DecimalField does the coercion)
        if value is None:
            raise serializers.ValidationError("Amount is required.")

        try:
            # Normalise — e.g. '10.0' → Decimal('10.0')
            amount = Decimal(str(value))
        except InvalidOperation:
            raise serializers.ValidationError("Enter a valid monetary amount.")

        if amount <= Decimal("0"):
            raise serializers.ValidationError("Amount must be greater than zero.")

        if amount < Decimal("0.01"):
            raise serializers.ValidationError("Minimum amount is ₹0.01.")

        if amount > Decimal("99999999.99"):
            raise serializers.ValidationError("Amount exceeds the maximum allowed value (₹99,999,999.99).")

        # Guard against excessive decimal precision (e.g. 10.001)
        sign, digits, exponent = amount.as_tuple()
        if exponent < -2:
            raise serializers.ValidationError(
                "Amount cannot have more than 2 decimal places."
            )

        return amount

    def validate_description(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Description cannot be blank.")
        if len(value) > 500:
            raise serializers.ValidationError("Description cannot exceed 500 characters.")
        return value

    def validate_date(self, value):
        today = date.today()
        max_future = today + timedelta(days=365)

        if value > max_future:
            raise serializers.ValidationError(
                "Date cannot be more than one year in the future."
            )
        # Allow past dates freely — users may enter old receipts.
        return value

    def validate_idempotency_key(self, value):
        if value is None:
            return None
        # DRF UUIDField already validates UUID format; extra guard:
        try:
            return uuid.UUID(str(value))
        except ValueError:
            raise serializers.ValidationError("idempotency_key must be a valid UUID v4.")

    # ── Object-level validation ────────────────────────────────────────────────

    def validate(self, attrs):
        # Strip idempotency_key from attrs — it is not an Expense model field;
        # the view handles it separately.
        attrs.pop("idempotency_key", None)
        return attrs


class CategorySummarySerializer(serializers.Serializer):
    """Read-only serializer for per-category totals returned by GET /expenses/summary/."""
    category = serializers.CharField()
    category_display = serializers.CharField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    count = serializers.IntegerField()