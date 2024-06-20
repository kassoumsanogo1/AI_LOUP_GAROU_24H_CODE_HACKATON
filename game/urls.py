from django.urls import path
from .views import play_game
from .views import home


urlpatterns = [
    path('', home, name='home'),
    path('play_game/', play_game, name='play_game'),
]
