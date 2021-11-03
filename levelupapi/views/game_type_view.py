from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from levelupapi.models import GameType
from rest_framework.status import HTTP_404_NOT_FOUND


class GameTypeView(ViewSet):

    def list(self, request):
        game_types = GameType.objects.all()

        game_types = GameTypeSerializer(game_types, many=True)

        return Response(game_types.data)

    def retrieve(self, request, pk):
        try:
            game_type = GameType.objects.get(pk=pk)
            game_type = GameTypeSerializer(game_type)

            return Response(game_type.data)
        except GameType.DoesNotExist:
            return Response({'message': 'Game Type does not exist'},
                status=HTTP_404_NOT_FOUND
            )


class GameTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameType
        fields =  ('label', 'id')