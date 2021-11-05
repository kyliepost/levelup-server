"""View module for handling requests about games"""
from django.core.exceptions import ValidationError
from rest_framework import status
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from levelupapi.models import Game, GameType, Gamer

class GameView(ViewSet):
    def create(self, request):
        gamer = Gamer.objects.get(user=request.auth.user)
        game_type = GameType.objects.get(pk=request.data['gameTypeId'])

        try:
            game = Game.objects.create(
                gamer=gamer,
                game_type=game_type,
                title=request.data['title'],
                maker=request.data['maker'],
                number_of_players=request.data['numberOfPlayers'],
                skill_level=request.data['skillLevel'],
            )

            game_serializer = GameSerializer(game, context={'request': request})
            return Response(game_serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        games = Game.objects.all()

        game_type = request.query_params.get('gameType', None)
        if game_type is not None:
            games = games.filter(game_type__label=game_type)
        
        games_serializer = GameSerializer(games, many=True, context={'request': request})
        return Response(games_serializer.data)
    
    def retrieve(self, request, pk):
        try:
            game = Game.objects.get(pk=pk)
            game_serializer = GameSerializer(game, context={'request', request})
            return Response(game_serializer.data)
        except Game.DoesNotExist as ex:
            return Response({'message': 'Game does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk):
        try:
            game = Game.objects.get(pk=pk)
            game.title = request.data['title']
            game.maker = request.data['maker']
            game.number_of_players = request.data['numberOfPlayers']
            game.skill_level = request.data['skillLevel']
            game.game_type = GameType.objects.get(pk=request.data['gameTypeId'])
            game.save()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Game.DoesNotExist as ex:
            return Response({'message': 'Game does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        try:
            game = Game.objects.get(pk=pk)
            game.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Game.DoesNotExist:
            return Response({'message': 'Game not found'}, status=status.HTTP_404_NOT_FOUND)


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'title', 'maker', 'number_of_players', 'gamer']
        depth = 1