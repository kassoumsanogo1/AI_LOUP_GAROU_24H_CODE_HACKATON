from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .game_logic import start_game
from .forms import GameForm

def play_game(request):
    messages = []
    user_prompts = []
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            player_count = form.cleaned_data['player_count']
            discussion_depth = form.cleaned_data['discussion_depth']
        #render_markdown = form.cleaned_data['render_markdown']
            real_player_name = form.cleaned_data['real_player_name']
            #role_choice = request.POST.get('role_choice', "")
            messages, user_prompts = start_game(player_count, discussion_depth, real_player_name)
            #game = start_game(player_count=player_count, discussion_depth=discussion_depth, real_player_name=real_player_name)
    else:
        form = GameForm()
    return render(request, 'game/play_game.html', {'form': form, 'messages': messages, 'user_prompts': user_prompts})


def home(request):
    return render(request, 'game/home.html')