"""
filters.py — query-parameter filtering for GET /expenses/

Supported params:
  ?category=food           — exact match against Category choices
  ?sort=date_desc          — newest date first (default behaviour)
  ?sort=date_asc           — oldest date first
  ?date_from=YYYY-MM-DD    — include expenses on or after this date
  ?date_to=YYYY-MM-DD      — include expenses on or before this date

"""

import django_filters
from django.db import models as db_models

from .models import Category, Expense


class ExpenseFilter(django_filters.FilterSet):
    category = django_filters.ChoiceFilter(choices=Category.choices)

    # Date range filters — let users narrow down a period
    date_from = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = Expense
        fields = ["category", "date_from", "date_to"]


SORT_MAP = {
    "date_desc": ["-date", "-created_at"],   # newest expense-date first (default)
    "date_asc":  ["date", "created_at"],     # oldest expense-date first
}

DEFAULT_SORT = "date_desc"


def apply_sort(queryset, sort_param: str):
    """
    Apply ordering from a safe allow-list.
    Unknown values are silently ignored and fall back to the default.
    """
    ordering = SORT_MAP.get(sort_param, SORT_MAP[DEFAULT_SORT])
    return queryset.order_by(*ordering)