from rest_framework import serializers
from .models import Help

class HelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Help
        fields = ['id', 'user', 'description', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']
