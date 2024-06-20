# game/forms.py
from django import forms

class GameForm(forms.Form):
    player_count = forms.IntegerField(label='Player Count', min_value=3, max_value=5)
    discussion_depth = forms.IntegerField(label='Discussion Depth', min_value=3)
    CHOICES = [('yes', 'Yes'), ('no', 'No')]
    participation = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect,
                                      label="Would you participate in Werewolf game board?")
    real_player_name = forms.CharField(max_length=100, required=False, label="What's your name?")
    #player_count = forms.IntegerField(label="Player count")
    #discussion_depth = forms.IntegerField(label="Discussion depth")
    #render_markdown = forms.BooleanField(required=False, label="Render Markdown")

    def clean(self):
        cleaned_data = super().clean()
        participation = cleaned_data.get('participation')
        real_player_name = cleaned_data.get('real_player_name')
        if participation == 'yes' and not real_player_name:
            self.add_error('real_player_name', 'This field is required if you participate.')
        return cleaned_data