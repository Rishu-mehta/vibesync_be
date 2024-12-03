from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import Room
from .serializers import RoomSerializer, SetVideoURLSerializer, JoinRoomSerializer
import random
import string


def generate_room_id():
    """Generate a unique room ID."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


class CreateRoom(APIView):
    def post(self, request):
        user = request.user
        room_id = generate_room_id()
        room = Room.objects.create(room_id=room_id, host_user=user)
        serializer = RoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)





class RoomDetails(APIView):
    def get(self, request, room_id):
        try:
            room = Room.objects.get(room_id=room_id)
            serializer = RoomSerializer(room)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)


class SetVideoURL(APIView):
    def post(self, request, room_id):
        try:
            room = Room.objects.get(room_id=room_id)
            serializer = SetVideoURLSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            room.video_url = serializer.validated_data['video_url']
            room.save()
            return Response({"message": "Video URL updated successfully."}, status=status.HTTP_200_OK)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
