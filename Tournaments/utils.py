# utils.py
from rest_framework.response import Response

def api_response(success, message, data=None, status=200):
    """
    Utility function to return a standardized API response.
    
    :param success: Boolean, True if the request was successful, False otherwise
    :param message: String, the message to return in the response
    :param data: Data to return in the response, can be None
    :param status: HTTP status code, defaults to 200 (OK)
    
    :return: DRF Response object with the specified structure
    """
    return Response({
        'success': success,
        'message': message,
        'data': data
    }, status=status)
