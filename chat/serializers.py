from rest_framework import serializers
from .models import ChatMessage
from users.models import User
from Tournaments.models import Game
from users.serializers import UserProfileSerializer


class ChatMessageSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    game = serializers.PrimaryKeyRelatedField(queryset=Game.objects.all())

    class Meta:
        model = ChatMessage
        fields = ['user', 'message', 'game']

    def to_representation(self, instance):
        # Customize the output format to include user and game details
        representation = super().to_representation(instance)
        representation['user'] = {
            'id': instance.user.id,
            'username': instance.user.username,  # Adjust based on your User model
        }
        representation['game'] = {
            'id': instance.game.id,
            'name': instance.game.name,  # Adjust based on your Game model
        }
        return representation
class ChatMessageSerializernew(serializers.ModelSerializer):
    user = UserProfileSerializer()
    username = serializers.CharField(source='user.username', read_only=True)
    game_name = serializers.CharField(source='game.name', read_only=True)
    game_image = serializers.CharField(source='game.image', read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['username', 'user','message', 'game_name','game_image', 'timestamp']