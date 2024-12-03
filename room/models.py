from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    room_id = models.CharField(max_length=10, unique=True)
    host_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    video_url = models.URLField(blank=True, null=True)
    current_video_time = models.FloatField(default=0.0)  # Tracks video playback position
    is_playing = models.BooleanField(default=False)  # Indicates if the video is playing
    video_quality = models.CharField(max_length=10, blank=True, null=True)  # Tracks current video quality
    members = models.ManyToManyField(User, related_name='rooms', blank=True)  # Room members

    def __str__(self):
        return self.room_id


class ChatMessage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} in {self.room.room_id} - {self.timestamp}"
