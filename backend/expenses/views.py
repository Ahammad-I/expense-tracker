"""
views.py — Expense Tracker API views

Endpoints:
  POST   /api/v1/expenses/           Create an expense (idempotent)
  GET    /api/v1/expenses/           List expenses (filterable, sortable)
  GET    /api/v1/expenses/categories/ List valid category choices
  GET    /api/v1/expenses/summary/   Total and count per category (for current filters)

 
"""

import uuid
import logging
from decimal import Decimal

from django.db import transaction, IntegrityError
from django.db.models import Sum, Count

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import ExpenseFilter, apply_sort
from .models import Category, Expense, IdempotencyKey
from .serializers import CategorySummarySerializer, ExpenseSerializer

logger = logging.getLogger(__name__)


class ExpenseListCreateView(APIView):
    """
    GET  /api/v1/expenses/  — list, filter, sort
    POST /api/v1/expenses/  — create (idempotent)
    """

    # ── GET ────────────────────────────────────────────────────────────────────

    def get(self, request):
        queryset = Expense.objects.all()

        # Apply category / date-range filters via django-filter
        filterset = ExpenseFilter(request.GET, queryset=queryset)
        if not filterset.is_valid():
            return Response(
                {"error": "Invalid filter parameters.", "details": filterset.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        queryset = filterset.qs

        # Apply sorting
        sort_param = request.GET.get("sort", "date_desc")
        queryset = apply_sort(queryset, sort_param)

        # Compute total BEFORE pagination (if we add it later)
        # Use SUM in the DB rather than summing in Python to avoid loading all rows.
        total = queryset.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        serializer = ExpenseSerializer(queryset, many=True)

        return Response(
            {
                "count": queryset.count(),
                "total": f"{total:.2f}",       # string to preserve decimal precision over JSON
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # ── POST ───────────────────────────────────────────────────────────────────

    def post(self, request):
        # ── 1. Extract idempotency key (header takes priority over body) ───────
        raw_key = (
            request.headers.get("Idempotency-Key")
            or request.data.get("idempotency_key")
        )

        idempotency_key = None
        if raw_key:
            try:
                idempotency_key = uuid.UUID(str(raw_key))
            except ValueError:
                return Response(
                    {"error": "Idempotency-Key must be a valid UUID."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # ── 2. Check for an existing idempotency record ────────────────────────
        if idempotency_key:
            try:
                existing = IdempotencyKey.objects.select_related("expense").get(
                    key=idempotency_key
                )
                if not IdempotencyKey.is_expired(existing):
                    # Return the original expense — do not create a duplicate
                    serializer = ExpenseSerializer(existing.expense)
                    response = Response(serializer.data, status=status.HTTP_200_OK)
                    response["X-Idempotent-Replay"] = "true"
                    return response
                # Key exists but is expired — fall through and create a new expense
            except IdempotencyKey.DoesNotExist:
                pass  # first time seeing this key — proceed normally

        # ── 3. Validate request body ───────────────────────────────────────────
        serializer = ExpenseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "error": "Validation failed. Please check the details below.",
                    "details": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── 4. Persist inside a transaction ───────────────────────────────────
        try:
            with transaction.atomic():
                expense = serializer.save()

                if idempotency_key:
                    IdempotencyKey.objects.create(
                        key=idempotency_key,
                        expense=expense,
                    )
        except IntegrityError as exc:
            # Race condition: two concurrent requests with the same idempotency key.
            # One succeeded; the other hits the unique constraint on IdempotencyKey.pk.
            logger.warning("Idempotency key race condition for key=%s: %s", idempotency_key, exc)
            try:
                existing = IdempotencyKey.objects.select_related("expense").get(
                    key=idempotency_key
                )
                serializer = ExpenseSerializer(existing.expense)
                response = Response(serializer.data, status=status.HTTP_200_OK)
                response["X-Idempotent-Replay"] = "true"
                return response
            except IdempotencyKey.DoesNotExist:
                logger.exception("Unexpected integrity error creating expense")
                return Response(
                    {"error": "An unexpected error occurred. Please try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        out_serializer = ExpenseSerializer(expense)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)


class CategoryListView(APIView):
    """
    GET /api/v1/expenses/categories/
    Returns all valid category choices so the frontend never hard-codes them.
    """

    def get(self, request):
        categories = [
            {"value": value, "label": label}
            for value, label in Category.choices
        ]
        return Response({"results": categories}, status=status.HTTP_200_OK)


class ExpenseSummaryView(APIView):
    """
    GET /api/v1/expenses/summary/?category=food&date_from=...&date_to=...

    Returns total amount and count per category for the currently filtered set.
    Accepts the same filter params as the list endpoint so the frontend can
    show a filtered summary in the 'nice-to-have' summary view.
    """

    def get(self, request):
        queryset = Expense.objects.all()

        filterset = ExpenseFilter(request.GET, queryset=queryset)
        if not filterset.is_valid():
            return Response(
                {"error": "Invalid filter parameters.", "details": filterset.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        queryset = filterset.qs

        summary = (
            queryset
            .values("category")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("-total")
        )

        # Attach human-readable labels
        category_map = dict(Category.choices)
        results = [
            {
                "category": row["category"],
                "category_display": category_map.get(row["category"], row["category"]),
                "total": row["total"],
                "count": row["count"],
            }
            for row in summary
        ]

        grand_total = queryset.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        serializer = CategorySummarySerializer(results, many=True)
        return Response(
            {
                "grand_total": f"{grand_total:.2f}",
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )