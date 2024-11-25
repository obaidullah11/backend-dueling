from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Help
from .serializers import HelpSerializer

class CreateHelpRequestView(APIView):
    """
    API to create a new Help request.
    """
    def post(self, request):
        serializer = HelpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Help request created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": "Invalid data.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
