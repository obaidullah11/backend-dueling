from django.urls import path
from . import views

urlpatterns = [
    path("initiate-payment/", views.initiate_payment, name="initiate_payment"),
    path("kpay-callback/", views.kpay_callback, name="kpay_callback"),
    path("verify-payment/", views.verify_payment, name="verify_payment"),
]
