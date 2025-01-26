import base64
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
from django.views.decorators.csrf import csrf_exempt

# KPay Credentials and Test Environment
TRAN_PORTAL_ID = "540801"
TRAN_PORTAL_PASSWORD = "540801pg"
RESOURCE_KEY = "9D2JJ07HA1Y47RF3"
BASE_URL = "https://kpaytest.com.kw"  # Test environment URL

# Utility function for basic authentication
def get_auth_header():
    credentials = f"{TRAN_PORTAL_ID}:{TRAN_PORTAL_PASSWORD}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded_credentials}"}

@api_view(['POST'])
def initiate_payment(request):
    try:
        # Parse the request body for payment details
        data = request.data

        # Extract payment parameters from the request data
        order_id = data.get("order_id")
        amount = data.get("amount")
        customer_name = data.get("customer_name", "Guest")
        customer_email = data.get("customer_email", "")
        customer_phone = data.get("customer_phone", "")
        redirect_url = data.get("redirect_url", "")

        # Validate required parameters
        if not order_id or not amount:
            return Response({"error": "order_id and amount are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare payload for KPay API
        payload = {
            "terminal_id": TRAN_PORTAL_ID,
            "order_id": order_id,
            "amount": amount,
            "currency": "KWD",  # Adjust according to your payment gateway's requirements
            "redirect_url": redirect_url,
            "resource_key": RESOURCE_KEY,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "customer_phone": customer_phone,
        }

        # Get authentication headers
        headers = get_auth_header()
        headers.update({"Content-Type": "application/json"})

        # Send POST request to KPay API
        response = requests.post(
            f"{BASE_URL}/api/payment/initiate", json=payload, headers=headers
        )

        # Check if the KPay response is successful
        if response.status_code == 200:
            return Response(response.json(), status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to initiate payment", "details": response.text}, status=status.HTTP_400_BAD_REQUEST)

    except json.JSONDecodeError:
        # Handle invalid JSON format
        return Response({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        # Handle unexpected exceptions
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 2. Callback URL (Handle KPay redirect)
@csrf_exempt
def kpay_callback(request):
    if request.method == "POST" or request.method == "GET":
        try:
            # KPay will send the transaction status as query parameters or in body
            data = request.GET or request.POST
            order_id = data.get("order_id")
            status = data.get("transaction_status")
            transaction_id = data.get("transaction_id")

            return JsonResponse(
                {
                    "message": "Payment status received",
                    "order_id": order_id,
                    "transaction_status": status,
                    "transaction_id": transaction_id,
                },
                status=200,
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


# 3. Verify Payment Status API
@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            order_id = data.get("order_id")

            payload = {
                "terminal_id": TRAN_PORTAL_ID,
                "order_id": order_id,
                "resource_key": RESOURCE_KEY,
            }

            headers = get_auth_header()
            headers.update({"Content-Type": "application/json"})

            # Sending request to KPay API for payment verification
            response = requests.post(
                f"{BASE_URL}/api/payment/status", json=payload, headers=headers
            )

            # Return KPay verification response
            if response.status_code == 200:
                return JsonResponse(response.json(), status=200)
            else:
                return JsonResponse({"error": "Failed to verify payment"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
