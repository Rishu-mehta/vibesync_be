from rest_framework import serializers
from .models import Room
from django.contrib.auth.models import User

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['room_id', 'host_user', 'created_at', 'current_video_time', 'video_url']
        read_only_fields = ['room_id', 'host_user', 'created_at']

class SetVideoURLSerializer(serializers.Serializer):
    video_url = serializers.URLField(required=True)

class JoinRoomSerializer(serializers.Serializer):
    room_id = serializers.CharField(required=True)
