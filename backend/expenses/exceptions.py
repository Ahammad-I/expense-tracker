"""
exceptions.py — uniform error response shape

Every error response from this API has this shape:
{
    "error": "<short human-readable message>",
    "details": { "<field>": ["<message>", ...] }   ← only for validation errors
}

This makes it trivial for the frontend to display field-level errors
without parsing varying DRF error formats.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    # Let DRF build its default response first
    response = exception_handler(exc, context)

    if response is None:
        # Unhandled server error — let Django's 500 handler deal with it
        return None

    original_data = response.data

    if isinstance(original_data, dict):
        # Validation errors: {"field": ["msg"]} or {"non_field_errors": ["msg"]}
        non_field = original_data.pop("non_field_errors", [])
        detail = original_data.pop("detail", None)

        if detail:
            error_message = str(detail)
            details = {}
        elif non_field:
            error_message = non_field[0] if non_field else "Validation failed."
            details = original_data if original_data else {}
        else:
            error_message = "Validation failed. Please check the details below."
            details = original_data
    else:
        error_message = str(original_data)
        details = {}

    response.data = {
        "error": error_message,
        **({"details": details} if details else {}),
    }

    return response