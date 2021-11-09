"""View module for handling requests about games"""
from django.core.exceptions import ValidationError
from rest_framework import status
from django.contrib.auth import get_user_model
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from levelupapi.models import Game, Event, Gamer
from rest_framework.decorators import action


class EventView(ViewSet):
    """Level up games"""

    @action(methods=['post', 'delete'], detail=True)
    def signup(self, request, pk=None):
        """Managing gamers signing up for events"""
        gamer = Gamer.objects.get(user=request.auth.user)

        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response(
                {'message': 'Event does not exist.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == "POST":
            try:
                event.attendees.add(gamer)
                return Response({}, status=status.HTTP_201_CREATED)
            except Exception as ex:
                return Response({'message': ex.args[0]})

        elif request.method == "DELETE":
            try:
                event.attendees.remove(gamer)
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            except Exception as ex:
                return Response({'message': ex.args[0]})


    def create(self, request):
        """Handle POST operations
        Returns:
            Response -- JSON serialized game instance
        """

        gamer = Gamer.objects.get(user=request.auth.user)

        # Use the Django ORM to get the record from the database
        # whose `id` is what the client passed as the
        game = Game.objects.get(pk=request.data["gameId"])


        try:
            event = Event.objects.create(
                description=request.data["description"],
                date=request.data["date"],
                time=request.data["time"],
                organizer=gamer,
                game = game
            )
            serializer = EventSerializer(event, context={'request': request})
            return Response(serializer.data)

        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)



    def retrieve(self, request, pk=None):
        """Handle GET requests for single event
        Returns:
            Response -- JSON serialized event instance
        """
        try:
            event = Event.objects.get(pk=pk)
            serializer = EventSerializer(event, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests for a event
        Returns:
            Response -- Empty body with 204 status code
        """
        gamer = Gamer.objects.get(user=request.auth.user)
        game = Game.objects.get(pk=request.data["gameId"])

      
        event = Event.objects.get(pk=pk)
        event.description = request.data["description"]
        event.date = request.data["date"]
        event.time = request.data["time"]
        event.game = game
        event.organizer = gamer

        event.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single game
        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            event = Event.objects.get(pk=pk)
            event.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Event.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests to games resource
        Returns:
            Response -- JSON serialized list of games
        """
        # Get all game records from the database
        events = Event.objects.all()
        gamer = Gamer.objects.get(user=request.auth.user)
        game = self.request.query_params.get('gameId', None)


        for event in events:
            event.joined = gamer in event.attendees.all()

        if game is not None:
            events = events.filter(game__id=type)

        serializer = EventSerializer(
            events, many=True, context={'request': request})
        return Response(serializer.data)

class EventUserSerializer(serializers.ModelSerializer):
    class Meta: 
        model = get_user_model()
        fields = ['first_name', 'last_name']

class EventGamerSerializer(serializers.ModelSerializer):
    user = EventUserSerializer(many=False)
    class Meta:
        model = Gamer
        fields = ['user']

class EventSerializer(serializers.ModelSerializer):
    """JSON serializer for games
    
    Arguments:
        serializer type
    """
    joined = serializers.BooleanField(required=False)
    organizer = EventGamerSerializer(many=False)
    class Meta:
        model = Event
        fields = ('id', 'game', 'description', 'date', 'time', 'organizer', "attendees", "joined")
        depth = 1