from django.urls import path
from .views import CategoryListView, ExpenseListCreateView, ExpenseSummaryView

app_name = "expenses"

urlpatterns = [
    # Core CRUD
    path("expenses/", ExpenseListCreateView.as_view(), name="list-create"),

    # Helper: all valid category choices (so the frontend never hard-codes them)
    path("expenses/categories/", CategoryListView.as_view(), name="categories"),

    # Nice-to-have: per-category totals (accepts same filters as the list endpoint)
    path("expenses/summary/", ExpenseSummaryView.as_view(), name="summary"),
]
