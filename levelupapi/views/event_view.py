"""View module for handling requests about games"""
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User

from levelupapi.models import Gamer, Game, Event

class EventView(ViewSet):
    def create(self, request):
        organizer = Gamer.objects.get(user=request.auth.user)
        game = Game.objects.get(pk=request.data['gameId'])

        try:
            event = Event.objects.create(
                game=game,
                organizer=organizer,
                description=request.data['description'],
                date=request.data['date'],
                time=request.data['time']
            )
            event_serializer = EventSerializer(event, context={'request': request})
            return Response(event_serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        events = Event.objects.all()
        events_serializer = EventSerializer(events, many=True)
        return Response(events_serializer.data)
    
    def retrieve(self, request, pk):
        event = Event.objects.get(pk=pk)
        event_serializer = EventSerializer(event, context={'request': request})
        return Response(event_serializer.data)

    def destroy(self, request, pk):
        event = Event.objects.get(pk=pk)
        event.delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def update(self, request, pk):
        event = Event.objects.get(pk=pk)
        event.date = request.data['date']
        event.time = request.data['time']
        event.description = request.data['description']
        event.game = Game.objects.get(pk=request.data['gameId'])
        event.save()

        return Response(None, status=status.HTTP_204_NO_CONTENT)




class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

class GamerSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Gamer
        fields = ['user']


class EventSerializer(ModelSerializer):
    organizer = GamerSerializer()

    class Meta:
        model = Event
        fields = ['id', 'organizer', 'game', 'date', 'time', 'description']
        depth = 2
        