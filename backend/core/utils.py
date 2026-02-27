from rest_framework.response import Response
from rest_framework import status


def success_response(data=None, message: str = "", status_code: int = status.HTTP_200_OK) -> Response:
    payload: dict = {"success": True, "data": data}
    if message:
        payload["message"] = message
    return Response(payload, status=status_code)


def error_response(
    error: str,
    message: str,
    details: dict | None = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> Response:
    payload: dict = {"success": False, "error": error, "message": message}
    if details:
        payload["details"] = details
    return Response(payload, status=status_code)
