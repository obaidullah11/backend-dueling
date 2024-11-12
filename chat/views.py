# views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ChatMessage
from .serializers import ChatMessageSerializer,ChatMessageSerializernew
@api_view(['POST'])
def create_chat_message(request):
    serializer = ChatMessageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Chat message created successfully.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'message': 'Failed to create chat message.',
        'data': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def get_chat_messages_by_game(request, game_id):
    try:
        # Filter messages by game_id
        messages = ChatMessage.objects.filter(game_id=game_id)

        # Check if messages exist
        if not messages.exists():
            return Response({
                "success": False,
                "message": "No chat messages found for this game.",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the messages
        serializer = ChatMessageSerializernew(messages, many=True)

        return Response({
            "success": True,
            "message": "Chat messages retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "data": []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)