# urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *

urlpatterns = [
    path('notifications/<int:user_id>/', UserNotificationsAPIView.as_view(), name='user-notifications'),
    path('notifications/<int:user_id>/mark-read/', MarkNotificationsAsReadAPIView.as_view(), name='mark-notifications-read'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
