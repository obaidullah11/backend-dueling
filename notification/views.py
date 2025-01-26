from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Notification
from users.models import User
from .serializers import NotificationSerializer
from django.http import Http404
from rest_framework.exceptions import NotFound
class UserNotificationsAPIView(APIView):
    def get(self, request, user_id):
        try:
            # Check if the user exists
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            # Custom error response if user is not found
            return Response({
                "success": False,
                "message": "User not found.",
                "data": None
            }, status=status.HTTP_200_OK)

        # Get all notifications for the user
        notifications = Notification.objects.filter(user=user)

        if not notifications.exists():
            return Response({
                "success": False,
                "message": "No notifications found for this user.",
                "data": []
            }, status=status.HTTP_200_OK)

        # Serialize the notifications
        serializer = NotificationSerializer(notifications, many=True)

        return Response({
            "success": True,
            "message": "Notifications retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

# class UserNotificationsAPIView(APIView):
#     def get(self, request, user_id):
#         # Check if the user exists
#         user = get_object_or_404(User, id=user_id)
#         # Get all notifications for the user
#         notifications = Notification.objects.filter(user=user)
#         # Serialize the notifications
#         serializer = NotificationSerializer(notifications, many=True)

#         # Custom response structure
#         return Response({
#             "success": True,
#             "message": "Notifications retrieved successfully",
#             "data": serializer.data
#         }, status=status.HTTP_200_OK)
# class MarkNotificationsAsReadAPIView(APIView):
#     def put(self, request, user_id):
#         # Check if the user exists
#         user = get_object_or_404(User, id=user_id)
#         # Update all notifications for the user
#         updated_count = Notification.objects.filter(user=user, is_read=False).update(is_read=True)

#         # Custom response structure
#         return Response({
#             "success": True,
#             "message": f"{updated_count} notifications marked as read",
#             "data": None
#         }, status=status.HTTP_200_OK)



class MarkNotificationsAsReadAPIView(APIView):
    def put(self, request, user_id):
        # Check if the user exists
        user = get_object_or_404(User, id=user_id)
        # Update all unread notifications for the user
        updated_count = Notification.objects.filter(user=user, is_read=False).update(is_read=True)

        # Response based on whether any notifications were updated
        if updated_count == 0:
            return Response({
                "success": False,
                "message": "No unread notifications found to mark as read.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "success": True,
            "message": f"{updated_count} notifications marked as read.",
            "data": None
        }, status=status.HTTP_200_OK)
