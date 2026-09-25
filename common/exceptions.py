from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler ensuring standard JSON error format across all API endpoints:
    {
        "success": false,
        "message": "Human readable summary error message",
        "errors": { ... detailed field or error dict ... }
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        message = "An error occurred processing your request."
        
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                message = str(response.data['detail'])
            elif 'non_field_errors' in response.data:
                errors_list = response.data['non_field_errors']
                if isinstance(errors_list, list) and errors_list:
                    message = str(errors_list[0])
                else:
                    message = str(errors_list)
            else:
                first_key = next(iter(response.data))
                first_val = response.data[first_key]
                if isinstance(first_val, list) and len(first_val) > 0:
                    message = f"{first_key}: {first_val[0]}"
                else:
                    message = f"{first_key}: {first_val}"
        elif isinstance(response.data, list):
            if len(response.data) > 0:
                message = str(response.data[0])

        custom_data = {
            'success': False,
            'message': message,
            'errors': response.data
        }

        response.data = custom_data

    return response
