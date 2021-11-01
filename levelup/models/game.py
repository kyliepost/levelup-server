from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):

    game_type = models.ForeignKey("GameType", on_delete=models.CASCADE)
    title = models.CharField(max_length=55)
    maker = models.CharField(max_length=55)
    gamer = models.ForeignKey("Gamer", on_delete=models.CASCADE) 
    number_of_players = models.IntegerField(_(""))
    skill_level = models.IntegerField()

