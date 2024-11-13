from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from users.views import UserDetailViewnew,UserDetailView,UpdatePasswordViewnew,UseradminLoginView,ResendOTPView,set_new_password,SocialLoginOrRegisterView,SendPasswordResetEmailView,VerifyOTP,list_users,UserUpdateAPIView, UserChangePasswordView, UserLoginView, UserProfileView, UserRegistrationView,UserDeleteAPIView, UserPasswordResetView
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('admin/login/', UseradminLoginView.as_view(), name='login'),

    path('me/', UserProfileView.as_view(), name='profile'),
    path('changepassword/<str:custom_id>/', UserChangePasswordView.as_view(), name='change-password'),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset-password'),
    path('account/activation/', VerifyOTP.as_view(), name='verify_otp'),
    path('updateProfile/<str:custom_id>/', UserUpdateAPIView.as_view(), name='user-update'),
    path('delete/<str:custom_id>/', UserDeleteAPIView.as_view(), name='user-delete'),
    path('getallusers/', list_users, name='list_users'),
    path('social/<str:custom_id>/', UserDetailViewnew.as_view(), name='user_detail'),
    path('forgotpassword/', set_new_password, name='set_new_password'),
    path('resend_otp/', ResendOTPView.as_view(), name='resend_otp'),
    path('api/social_login_or_register/', SocialLoginOrRegisterView.as_view(), name='social_login_or_register'),
    path('user/<str:id>/', UserDetailView.as_view(), name='user_detail'),
    path("update-password/", UpdatePasswordViewnew.as_view(), name="update-password"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)