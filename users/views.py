from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from users.serializers import UserUpdateSerializer,SendPasswordResetEmailSerializer,DriverSerializer, UserChangePasswordSerializer, UserLoginSerializer, UserPasswordResetSerializer, UserProfileSerializer, UserRegistrationSerializer
from django.contrib.auth import authenticate
from users.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import User
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .serializers import UserSerializer,SocialRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,PasswordResetSerializer
from django.contrib.auth.hashers import make_password
import random
from rest_framework.exceptions import ValidationError
import string
# class UserDetailViewnew(APIView):
#     # Specify that the view should use 'custom_id' for lookups
#     lookup_field = 'custom_id'

#     def get(self, request, custom_id):
#         try:
#             # Retrieve the user using the custom_id field
#             user = User.objects.get(custom_id=custom_id)
#             serializer = UserSerializer(user)
#             response_data = {
#                 "success": True,
#                 "message": "User data retrieved successfully.",
#                 "data": serializer.data
#             }
#             return Response(response_data, status=status.HTTP_200_OK)
#         except User.DoesNotExist:
#             response_data = {
#                 "success": False,
#                 "message": "User not found.",
#                 "data": None
#             }
#             return Response(response_data, status=status.HTTP_404_NOT_FOUND)
class SocialLoginOrRegisterView(APIView):
    def post(self, request):
        serializer = SocialRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            if not user.id:
                # If the user doesn't have an ID, retrieve by email
                email = request.data.get('email')  # Get email from request
                user_by_email = get_object_or_404(User, email=email)
                user = user_by_email  # Use the user retrieved by email

            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Determine if the user was newly created or logged in
            if user.pk:  # If user exists (logged in)
                message = 'User logged in successfully.'
            else:  # If user is newly created (registered)
                message = 'User registered successfully.'

            return Response({
                'success': True,
                'message': message,
                'data': {
                    'refresh': str(refresh),
                    'access': access_token,
                    'id': user.id,
                    'user': serializer.data
                }
            }, status=status.HTTP_200_OK)

        return Response({
            'success': False,
            'message': 'Failed to register or log in user.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)




class ResendOTPView(APIView):
    def post(self, request, format=None):
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Generate 4-digit API code
        api_code = get_random_string(length=4, allowed_chars='0123456789')

        # Update the user's OTP code
        user.otp_code = api_code
        user.save()

        # Send email to the user
        subject = 'Your 4-digit API'
        message = f'Your 4-digit API is: {api_code}'
        from_email = 'muhammadobaidullah1122@gmail.com'  # Update with your email
        to_email = user.email
        try:
            send_mail(subject, message, from_email, [to_email])
            return Response({'success': True, 'message': 'OTP resent successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Failed to resend OTP email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
def generate_random_password(length=8):
    # Generate a random 8-digit password
    return ''.join(random.choices(string.digits, k=length))

@api_view(['POST'])
def set_new_password(request):
    if request.method == 'POST':
        email = request.data.get('email')

        # Retrieve the user object from the database
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'No user found with this email.'}, status=400)

        # Generate a new random password
        new_password = generate_random_password()

        # Hash the new password before saving it
        hashed_password = make_password(new_password)

        # Update the user's password in the database
        user.password = hashed_password
        user.save()

        # Send the new password to the user's email
        subject = 'Your New Password'
        message = f'Your new password is: {new_password}'
        from_email = 'your@example.com'
        to_email = email
        try:
            send_mail(subject, message, from_email, [to_email])
            return JsonResponse({'success': True, 'message': 'Password  successfully  sent to the registered  email.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'message': 'Method not allowed.'}, status=405)




class UserDeleteAPIView(APIView):
    def delete(self, request, custom_id, format=None):
        try:
            user = User.objects.get(id=custom_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Log user details before deletion
        print(f"Deleting user: {user.username} (Custom ID: {user.id})")

        # Delete the user
        user.delete()

        return Response({'success': True, 'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
def send_verification_email(user_id):
    """
    Send a verification email containing a 4-digit code to the user's email address
    and update the user's OTP field with the generated code.

    Args:
        user_id (int): ID of the user to send the verification email to.

    Returns:
        bool: True if email is sent successfully and user's OTP field is updated, False otherwise.
    """
    try:
        # Retrieve user object using user ID
        user = User.objects.get(id=user_id)

        # Generate a 4-digit verification code
        verification_code = get_random_string(length=4, allowed_chars='0123456789')

        # Compose email details
        subject = 'Your 4-digit Verification Code'
        message = f'Your 4-digit verification code is: {verification_code}'
        from_email = "muhammadobaidullah1122@gmail.com"
        to_email = user.email

        # Send email
        send_mail(subject, message, from_email, [to_email])

        # Update user's OTP field with the generated verification code
        user.otp_code = verification_code
        user.save()

        return True
    except User.DoesNotExist:
        print(f"User with ID {user_id} does not exist")
        return False
    except Exception as e:
        print(f"Failed to send verification email: {e}")
        return False
# Generate Token Manually
def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)
  return {
      'refresh': str(refresh),
      'access': str(refresh.access_token),
  }
class PasswordResetAPIView(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user  # Assuming the user is authenticated and making the request
        user.password = make_password(serializer.validated_data['password'])
        user.save()

        return Response({'success': True, 'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
@api_view(['GET'])
def list_users(request):
    # Query all users from the database
    all_users = User.objects.all()

    # Serialize the queryset of users
    serializer = UserProfileSerializer(all_users, many=True)

    # Return serialized data in the response
    return Response(serializer.data)
# from users.utils import get_tokens_for_user
class UserUpdateAPIView(APIView):
    def post(self, request, custom_id, format=None):
        try:
            user = User.objects.get(id=custom_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Serialize data
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'User data updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class UserDetailView(APIView):
    # Explicitly tell DRF to look for custom_id instead of the default id field
    lookup_field = 'custom_id'

    def get(self, request, custom_id):
        try:
            # Fetch the user by custom_id
            user = User.objects.get(custom_id=custom_id)
            serializer = UserSerializer(user)

            # Structure the response
            response_data = {
                "success": True,
                "message": "User data retrieved successfully.",
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            response_data = {
                "success": False,
                "message": "User not found.",
                "data": None
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
class UserDetailViewnew(APIView):
    # Explicitly tell DRF to look for custom_id instead of the default id field
    lookup_field = 'custom_id'

    def get(self, request, custom_id):
        try:
            # Fetch the user by custom_id
            user = User.objects.get(id=custom_id)
            serializer = UserSerializer(user)

            # Structure the response
            response_data = {
                "success": True,
                "message": "User data retrieved successfully.",
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            response_data = {
                "success": False,
                "message": "User not found.",
                "data": None
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
# class UserRegistrationView(APIView):
#     renderer_classes = [UserRenderer]

#     def post(self, request, format=None):
#         serializer = UserRegistrationSerializer(data=request.data)

#         try:
#             serializer.is_valid(raise_exception=True)
#         except ValidationError as e:
#             error_detail = e.detail
#             if 'email' in error_detail:
#                 return Response({'success': False, 'error': "User with this Email already exists."}, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 return Response({'success': False, 'error': error_detail}, status=status.HTTP_400_BAD_REQUEST)

#         to_email = request.data.get('email')

#         # Save user data
#         user = serializer.save()
#         print(f"User {to_email} saved successfully.")

#         # Generate 4-digit API code
#         api_code = get_random_string(length=4, allowed_chars='0123456789')
#         # print(f"Generated API code: {request.data.email}")

#         # Send email to the user
#         subject = 'Your 4-digit API'
#         message = f'Your 4-digit API is: {api_code}'
#         from_email = 'muhammadobaidullah1122@gmail.com'  # Update with your email
#         to_email = to_email
#         try:
#             send_mail(subject, message, from_email, [to_email])
#             print(f"OTP email sent to {to_email}.")
#         except Exception as e:
#             # If sending email fails, return failure response
#             print(f"Failed to send OTP email to {to_email}. Error: {e}")
#             return Response({'success': False, 'message': 'Failed to send OTP email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return Response({'success': True, 'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)
# class UserRegistrationView(APIView):
#     renderer_classes = [UserRenderer]

#     def post(self, request, format=None):
#         serializer = UserRegistrationSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         to_email=request.data.get('email')

#         # Save user data
#         # user = serializer.save()
#         print(f"User {to_email} saved successfully.")

#         # Generate 4-digit API code
#         api_code = get_random_string(length=4, allowed_chars='0123456789')
#         # print(f"Generated API code: {request.data.email}")

#         # Send email to the user
#         subject = 'Your 4-digit API'
#         message = f'Your 4-digit API is: {api_code}'
#         from_email = 'muhammadobaidullah1122@gmail.com'  # Update with your email
#         to_email = to_email
#         try:
#             send_mail(subject, message, from_email, [to_email])
#             print(f"OTP email sent to {to_email}.")
#         except Exception as e:
#             # If sending email fails, return failure response
#             print(f"Failed to send OTP email to {to_email}. Error: {e}")
#             return Response({'success': False, 'message': 'Failed to send OTP email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Update OTP code in the user model
        # otp_code = api_code
        # user = serializer.save(otp_code=api_code)

        # # Get tokens for user
        # token = get_tokens_for_user(user)
        # print(f"Tokens generated for user {user.username}.")

        # Response indicating success and message
        # return Response({'success': True, 'message': 'User registered successfully. OTP sent to your email'}, status=status.HTTP_201_CREATED)
class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            error_detail = e.detail
            if 'email' in error_detail:
                return Response({'success': False, 'error': "User with this Email already exists."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'success': False, 'error': error_detail}, status=status.HTTP_400_BAD_REQUEST)

        to_email = request.data.get('email')

        # Generate 4-digit API code
        api_code = get_random_string(length=4, allowed_chars='0123456789')
        otp_code = api_code

        # Save user data with the OTP code
        user = serializer.save(otp_code=otp_code)
        print(f"User {to_email} saved successfully with OTP code {otp_code}.")

        # Send email to the user
        subject = 'Your 4-digit API'
        message = f'Your 4-digit API is: {api_code}'
        from_email = 'muhammadobaidullah1122@gmail.com'  # Update with your email
        try:
            send_mail(subject, message, from_email, [to_email])
            print(f"OTP email sent to {to_email}.")
        except Exception as e:
            # If sending email fails, return failure response
            print(f"Failed to send OTP email to {to_email}. Error: {e}")
            return Response({'success': False, 'message': 'Failed to send OTP email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Get tokens for user
        token = get_tokens_for_user(user)
        print(f"Tokens generated for user {user.username}.")

        # Response indicating success and message
        return Response({
            'success': True,
            'message': 'User registered successfully. OTP sent to your email.',

        }, status=status.HTTP_201_CREATED)
class VerifyOTP(APIView):
    def post(self, request):
        code = request.data.get('code')

        if not code:
            return Response({'success': False, 'error': 'Verification code is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the user based on the provided OTP code
            user = User.objects.get(otp_code=code)
        except User.DoesNotExist:
            return Response({'success': False, 'error': 'Please enter correct OTP code. Thank you'}, status=status.HTTP_404_NOT_FOUND)

        # Now you have the user based on the OTP code
        # Proceed with your verification process

        # Update the 'verify' field to True
        user.verify = True
        user.save()

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Modify response message to include user ID
        return Response({
            'success': True,
            'message': 'Verification successful',
            'token': access_token,
            'refresh': str(refresh),
            'user_id': user.id  # Include user ID in the response
        }, status=status.HTTP_200_OK)
# class UserLoginView(APIView):
#   renderer_classes = [UserRenderer]
#   def post(self, request, format=None):
#     serializer = UserLoginSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#     email = serializer.data.get('email')
#     password = serializer.data.get('password')
#     user = authenticate(email=email, password=password)
#     if user is not None:
#       token = get_tokens_for_user(user)
#       return Response({'token':token, 'msg':'Login Success'}, status=status.HTTP_200_OK)
#     else:
#       return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)


# class UserLoginView(APIView):
#     def post(self, request, format=None):
#         serializer = UserLoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         email = serializer.data.get('email')
#         password = serializer.data.get('password')
#         user = authenticate(email=email, password=password)
#         if user is not None:
#             refresh = RefreshToken.for_user(user)
#             token = str(refresh.access_token)
#             profile_serializer = UserProfileSerializer(user)
#             return Response({'success': True, 'id': user.id, 'token': token, 'profile': profile_serializer.data}, status=status.HTTP_200_OK)
#         else:
#             return Response({'success': False, 'errors': {'non_field_errors': ['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)
class UpdatePasswordViewnew(APIView):
    def post(self, request):
        email = request.data.get("email")
        new_password = request.data.get("new_password")

        if not email or not new_password:
            return Response(
                {"error": "Email and new password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)  # Use set_password to properly hash the password
            user.save()
            return Response(
                {"success": "Password updated successfully."},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
class UseradminLoginView(APIView):
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Email or Password is not valid.'
            }, status=status.HTTP_200_OK)

        # Check if user is verified



        # Authenticate user
        user = authenticate(username=email, password=password)  # Use email as username for authentication

        if user is not None:
            # Check if the user is an admin
            if user.user_type != 'admin':
                return Response({
                    'success': False,
                    'message': 'Access denied. Only admin users can log in here.'
                }, status=status.HTTP_200_OK)

            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)
            profile_serializer = UserProfileSerializer(user)  # Serialize User instance if needed

            return Response({
                'success': True,
                'is_verified': user.verify,
                'id': user.id,
                'token': token,
                'profile': profile_serializer.data if profile_serializer else None,
                'message': 'Login successful.'
            }, status=status.HTTP_200_OK)

        else:
            return Response({
                'success': False,
                'message': 'Email or Password is not valid.'
            }, status=status.HTTP_200_OK)
class UserLoginView(APIView):
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Email or Password is not valid.'
            }, status=status.HTTP_200_OK)

        # Check if user is verified
        if not user.verify:
            return Response({
                'success': False,
                'is_verified':user.verify,
                'message': 'Account is not verified. Please verify your email.'
            }, status=status.HTTP_200_OK)
        if not user.is_active:
            return Response({
                'success': False,
                'is_verified':user.verify,
                'is_active':user.is_active,
                'message': 'Account has been deactivated by Admin'
            }, status=status.HTTP_200_OK)
        # Authenticate user
        user = authenticate(username=email, password=password)  # Use email as username for authentication

        if user is not None:
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)
            profile_serializer = UserProfileSerializer(user)  # Serialize User instance if needed
            return Response({
                'success': True,
                'is_verified':user.verify,
                'id': user.id,
                'token': token,
                'profile': profile_serializer.data if profile_serializer else None,  # Include profile data if needed
                'message': 'Login successful.'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Email or Password is not valid.'
            }, status=status.HTTP_200_OK)

class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            serializer = UserProfileSerializer(request.user)
            return Response({
                "success": True,
                "message": "User profile retrieved successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "message": f"An error occurred: {str(e)}",
                "data": {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class UserChangePasswordView(APIView):
    def post(self, request, custom_id, format=None):
        try:
            # Retrieve the user based on the custom_id
            user = User.objects.get(id=custom_id)
        except User.DoesNotExist:
            # If user does not exist, return error response
            return Response({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Initialize the serializer with user context and request data
        serializer = UserChangePasswordSerializer(data=request.data, context={'user': user})

        # Validate the serializer data
        if serializer.is_valid():
            # Save the validated serializer (which updates the user's password)
            serializer.save()
            # Return success response if password changed successfully
            return Response({'success': True, 'message': 'Password changed successfully'}, status=status.HTTP_200_OK)

        # Return error response if serializer data is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# class UserChangePasswordView(APIView):
#   renderer_classes = [UserRenderer]
#   permission_classes = [IsAuthenticated]
#   def post(self, request, format=None):
#     serializer = UserChangePasswordSerializer(data=request.data, context={'user':request.user})
#     serializer.is_valid(raise_exception=True)
#     return Response({'msg':'Password Changed Successfully'}, status=status.HTTP_200_OK)

class SendPasswordResetEmailView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    serializer = SendPasswordResetEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Reset link send. Please check your Email'}, status=status.HTTP_200_OK)

class UserPasswordResetView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, uid, token, format=None):
    serializer = UserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token})
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Reset Successfully'}, status=status.HTTP_200_OK)


class DriverListAPIView(APIView):
    def get(self, request):
        drivers = User.objects.filter(role='Driver')
        serializer = DriverSerializer(drivers, many=True)
        return Response(serializer.data)

@api_view(['POST'])
def set_user_deleted(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user.is_deleted = True
    user.save()

    return Response({'message': f'Your account has been deleted'})