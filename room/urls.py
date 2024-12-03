from django.urls import path
from .views import CreateRoom, RoomDetails,SetVideoURL

urlpatterns = [
    path('create-room/', CreateRoom.as_view(), name='create-room'),
    path('room/<str:room_id>/', RoomDetails.as_view(), name='room-details'),
    path('room/<str:room_id>/set-video/', SetVideoURL.as_view(), name='set-video-url'),

]
