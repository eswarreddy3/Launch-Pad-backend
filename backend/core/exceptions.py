from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        error = response.data.get("detail", str(exc))
        response.data = {
            "success": False,
            "error": str(error),
            "message": str(error),
        }
        # Attach field-level validation errors if present
        if isinstance(response.data.get("details"), dict):
            response.data["details"] = response.data["details"]
    return response
