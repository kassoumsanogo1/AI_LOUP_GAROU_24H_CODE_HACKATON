import json
import random
import time, datetime
import requests

headers = {"Authorization": "Bearer *************************"}
current_model_number = 0
total_model_number = 5

global timerOn
timerOn = datetime.datetime.now()

def query(payload):
    time.sleep(0.5)
    if (current_model_number % total_model_number == 0):
        API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
    elif (current_model_number % total_model_number == 1):
        API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
    elif (current_model_number % total_model_number == 2):
        API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
    elif (current_model_number % total_model_number == 3):
        API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
    elif (current_model_number % total_model_number == 4):
        API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    global model
    model = API_URL.split("https://api-inference.huggingface.co/models/")[1]
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Échec de la requête HTTP : {e}")
        return {}

def return_dict_from_json_or_fix(message_json):
    global timerOn
    payload = {
        "inputs": f"Please just extract the JSON. The original message that contains the bad JSON is: \n {message_json}",
        "parameters": {
            "max_new_tokens": 600,  # Augmentez cette valeur selon vos besoins
            "repetition_penalty": 1.1,

        }
        }
    response = query(payload)
    if not response or not isinstance(response, list) or 'generated_text' not in response[0]:
        print(f"Unexpected or empty response from API: {response}")
        global current_model_number
        current_model_number += 1
        if datetime.datetime.now() - timerOn > datetime.timedelta(seconds=30):
            if '"voted_player"' in message_json:
                return json.loads(
                    '{"voted_player": "?", "reasoning": "This person made a statement that could potentially introduce doubt among the group and increase the likelihood that a werewolf will reveal themselves. As I don\'t have specific information to prove this, I am making an educated guess and choosing the player who made a statement that potentially could aid a werewolf\'s cause."}')
            elif '"statement"' in message_json:
                return json.loads(
                    '{"statement": "I woke up this morning feeling refreshed and ready to help my fellow villagers. I\'ve been a farmer my whole life and I know that the key to a successful harvest is working together and trusting each other.", "reasoning": "I want to convey that I am a benevolent Villager who is fully committed to the team\'s values. By talking about cooperation and trust, I am trying to create a positive image of myself and make the other players believe that I\'m not a Werewolf."}')
            elif '"choice"' in message_json:
                return json.loads(
                    '{"reasoning": "I want to convey that I am a benevolent Villager who is fully committed to the team\'s values. By talking about cooperation and trust, I am trying to create a positive image of myself and make the other players believe that I\'m not a Werewolf.", "choice": "§"}')
        return return_dict_from_json_or_fix(message_json)

    fixed_json = response[0]['generated_text']
    temp_fixed_json = fixed_json.split('{')
    list_of_responses = []
    for k in range(1, len(temp_fixed_json)):
        if (("}" in temp_fixed_json[k]) and ('reasoning' in temp_fixed_json[k]) and (
                ('statement' in temp_fixed_json[k]) or ('voted_player' in temp_fixed_json[k])) and (
                "[statement]" not in temp_fixed_json[k]) and ("[reasoning]" not in temp_fixed_json[k]) and (
                "middle_card" not in temp_fixed_json[k]) and ("Player name" not in temp_fixed_json[k])):
            list_of_responses.append(temp_fixed_json[k].split('}')[0])

    for k in range(len(list_of_responses)):
        list_of_responses[k] = '{' + list_of_responses[k] + '}'
    if list_of_responses:
        fixed_json = random.choice(list_of_responses)
        if (("}" in fixed_json) and ('reasoning' in fixed_json) and (
                ('statement' in fixed_json) or ('voted_player' in fixed_json)) and (
                "[statement]" not in fixed_json) and ("[reasoning]" not in fixed_json) and (
                "middle_card" not in fixed_json) and ("Player name" not in fixed_json)):
            if "None" in fixed_json:
                return return_dict_from_json_or_fix(message_json)
            else:
                return json.loads(fixed_json)
        else:

            return return_dict_from_json_or_fix(message_json)
    else:
        current_model_number += 1
        if datetime.datetime.now() - timerOn > datetime.timedelta(seconds=30):
            if '"voted_player"' in message_json:
                return json.loads(
                    '{"voted_player": "?", "reasoning": "This person made a statement that could potentially introduce doubt among the group and increase the likelihood that a werewolf will reveal themselves. As I don\'t have specific information to prove this, I am making an educated guess and choosing the player who made a statement that potentially could aid a werewolf\'s cause."}')
            elif '"statement"' in message_json:
                return json.loads(
                    '{"statement": "I woke up this morning feeling refreshed and ready to help my fellow villagers. I\'ve been a farmer my whole life and I know that the key to a successful harvest is working together and trusting each other.", "reasoning": "I want to convey that I am a benevolent Villager who is fully committed to the team\'s values. By talking about cooperation and trust, I am trying to create a positive image of myself and make the other players believe that I\'m not a Werewolf."}')
            elif '"choice"' in message_json:
                return json.loads(
                    '{"reasoning": "I want to convey that I am a benevolent Villager who is fully committed to the team\'s values. By talking about cooperation and trust, I am trying to create a positive image of myself and make the other players believe that I\'m not a Werewolf.", "choice": "§"}')
        return return_dict_from_json_or_fix(message_json)

class Player:

    def __init__(self, player_name, player_number, other_players, card, card_list):
        self.player_number = player_number
        self.player_name = player_name
        self.other_players = other_players
        self.card = card
        self.card_thought = card
        self.display_card = card
        self.rules_prompt_prefix = open('prompts/rules.txt').read().format(player_name=player_name,
                                                                           other_players='; '.join(other_players),
                                                                           card=card, card_list=card_list)
        self.memory = []

    def append_memory(self, memory_item):
        self.memory.append(memory_item)

    def run_prompt(self, prompt):
        full_prompt = self.rules_prompt_prefix

        if len(self.memory) > 0:
            full_prompt += '\n\nYou have the following memory of interactions in this game: \n\n' + '\n\n'.join(
                self.memory)
        full_prompt += prompt
        payload = {"inputs": full_prompt}
        response = query(payload)
        if not response:
            print("Received an empty response from the API.")
            return ""
        if not isinstance(response, list) or 'generated_text' not in response[0]:
            print(f"Unexpected response format: {response}")
            return ""
        return response[0]['generated_text']


class WebRenderingEngine:
    def __init__(self):
        self.messages = []
        self.user_prompts = []

    def get_player_colored_name(self, player):
        return f'{player.player_name}'

    def type_line(self, text):
        self.messages.append(text)

    def render_system_message(self, statement, ref_players=[], ref_cards=[]):
        ref_players_formatted = []
        for player in ref_players:
            ref_players_formatted.append(self.get_player_colored_name(player))
        ref_cards_formatted = []
        for card in ref_cards:
            ref_cards_formatted.append(f'{card}')
        self.messages.append(statement.format(ref_players=ref_players_formatted, ref_cards=ref_cards_formatted))

    def render_phase(self, phase):
        self.messages.append('')
        self.messages.append(f' THE {phase.upper()} PHASE WILL NOW BEGIN.')

    def render_game_statement(self, statement):
        self.messages.append(f'GAME : {statement}')

    def render_player_turn_init(self, player):
        self.messages.append(' ')
    def render_player_turn(self, player, statement, reasoning):
        self.messages.append(f'{self.get_player_colored_name(player)} reasoning : {reasoning}')
        if statement is not None:
            self.messages.append(f'{self.get_player_colored_name(player)} statement : {statement}')

    def render_player_vote(self, player, voted_player, reasoning):
        self.messages.append(f'{self.get_player_colored_name(player)} reasoning : {reasoning}')
        #self.type_line(reasoning)
        self.messages.append(f'{self.get_player_colored_name(player)} : I am voting for {voted_player}.')

    def render_vote_results(self, votes, players):
        self.messages.append('')
        self.messages.append('THE VOTES WERE :')
        for player in players:
            if votes[player.player_name] > 0:
                self.messages.append(f'{player.player_name} : {player.card} : {votes[player.player_name]}')

    def render_game_details(self, player_count, discussion_depth):
        self.messages.append(' ')
        self.messages.append('RUN DETAILS ')
        self.messages.append(f'PLAYER COUNT : {player_count}')
        self.messages.append(f'DISCUSSION DEPTH : {discussion_depth}')
        self.messages.append(f'BEST MODEL : {model}')

    def ask_user(self, prompt):
        self.user_prompts.append(prompt)
        self.messages.append(f'USER : {prompt}')

class Game:
    #Pas besoin de cette partie
    #Je peux supprimer role_choice
    def __init__(self, player_count, discussion_depth, real_player_name="", role_choice=""):
        self.player_count = player_count
        self.discussion_depth = discussion_depth
        self.card_list = None
        self.player_names = []
        self.players = []
        self.middle_cards = []
        self.real_player_name = real_player_name
        #self.role_choice = role_choice
        self.rendering_engine = WebRenderingEngine()

    def play(self):
        self.initialize_game()
        self.rendering_engine.render_system_message('WELCOME TO WEREWOLF GAME !')
        self.rendering_engine.render_system_message(self.card_list)
        self.introduce_players()
        self.show_middle_cards()
        self.rendering_engine.render_phase('NIGHT')
        self.rendering_engine.render_game_statement('EVERYONE, CLOSE YOUR EYES.')
        self.night_werewolf()
        self.night_seer()
        self.rendering_engine.render_phase('DAY')
        #Je peux supprimer cette partie
        #Sans dérangement
        self.rendering_engine.render_game_statement('EVERYONE, WAKE UP !')
        self.day()
        self.rendering_engine.render_phase('VOTE')
        self.vote()
        self.rendering_engine.render_game_details(self.player_count, self.discussion_depth)

# A toucher pour introduire le joueur dans le jeu
    #forcement modifier cette partie
    #Refais à neuf
    def initialize_game(self):
        if self.player_count < 3 or self.player_count > 5:
            raise ValueError('Number of players must be between 3 and 5 inclusive.')

        alloted_cards = ['Werewolf', 'Werewolf', 'Seer']

        while len(alloted_cards) < self.player_count + 3:
            alloted_cards.append('Villager')

        card_list = '* ' + '\n* '.join(alloted_cards)
        self.card_list = card_list

        random.shuffle(alloted_cards)

        self.player_names = self.get_player_names(self.player_count)
        if (self.real_player_name != ""):
            choice = input("Please, choise your role: Villager, Werewolf, Seer or Random: ")
            if (choice.lower() == 'random'):
                self.players = [
                    Player(name, i, self.get_other_players(i, self.player_names), alloted_cards[i - 1], card_list) for
                    i, name in enumerate(self.player_names, 1)]
            elif (choice.lower() == 'villager'):
                alloted_cards.remove("Villager")
                self.players.append(Player(self.real_player_name, 0,
                                           self.get_other_players(self.player_names.index(self.real_player_name),
                                                                  self.player_names), "Villager", card_list))
                for i in range(len(self.player_names)):
                    if (self.player_names != self.real_player_name):
                        self.players.append(
                            Player(self.player_names[i], i + 1, self.get_other_players(i, self.player_names),
                                   alloted_cards[i], card_list))
                alloted_cards.insert(0, "Villager")
            elif (choice.lower() == 'werewolf'):
                alloted_cards.remove("Werewolf")
                self.players.append(Player(self.real_player_name, 1,
                                           self.get_other_players(self.player_names.index(self.real_player_name),
                                                                  self.player_names), "Werewolf", card_list))
                for i in range(len(self.player_names)):
                    if (self.player_names != self.real_player_name):
                        self.players.append(
                            Player(self.player_names[i], i + 1, self.get_other_players(i, self.player_names),
                                   alloted_cards[i], card_list))
                alloted_cards.insert(0, "Werewolf")
            elif (choice.lower() == 'seer'):
                alloted_cards.remove("Seer")
                self.players.append(Player(self.real_player_name, 1,
                                           self.get_other_players(self.player_names.index(self.real_player_name),
                                                                  self.player_names), "Seer", card_list))
                for i in range(len(self.player_names)):
                    if (self.player_names != self.real_player_name):
                        self.players.append(
                            Player(self.player_names[i], i + 1, self.get_other_players(i, self.player_names),
                                   alloted_cards[i], card_list))
                alloted_cards.insert(0, "Seer")
        else:
            self.players = [
                Player(name, i, self.get_other_players(i, self.player_names), alloted_cards[i - 1], card_list) for
                i, name in enumerate(self.player_names, 1)]

        self.middle_cards = alloted_cards[self.player_count:]

    def introduce_players(self):
        for player in self.players:
            self.rendering_engine.render_system_message(
                f'Player number {player.player_number} is named {{ref_players[0]}}, and he has the {{ref_cards[0]}} card.',
                ref_players=[player], ref_cards=[player.card])

    def show_middle_cards(self):
        self.rendering_engine.render_system_message(
            'The cards face-down in the middle of the board are {ref_cards[0]}, {ref_cards[1]}, and {ref_cards[2]}.',
            ref_cards=self.middle_cards)

    def night_werewolf(self):
        self.rendering_engine.render_game_statement('Werewolves, wake up and look for other Werewolves.')
        werewolf_players = [player for player in self.players if player.card == 'Werewolf']

        if len(werewolf_players) == 0:
            self.rendering_engine.render_system_message('There are no werewolves in play.')
        elif len(werewolf_players) == 1:
            middle_card = random.choice(self.middle_cards)
            werewolf_players[0].append_memory(f'GAME: You are the only werewolf. You can deduce that the other werewolf card is in the middle cards. You randomly picked one of the center cards and were able to see that it was: {middle_card}')
            self.rendering_engine.render_system_message(
                'There is one werewolf in play, {ref_players[0]}. The werewolf wake up and search other werewolf.',
                ref_players=werewolf_players, ref_cards=[middle_card])
        else:
            for werewolf in werewolf_players:
                other_werewolf = [p for p in werewolf_players if p != werewolf][0]
                werewolf.append_memory(f'GAME: You have seen that the other werewolf is {other_werewolf.player_name}.')
            self.rendering_engine.render_system_message(
                'There are two werewolves in play, {ref_players[0]} and {ref_players[1]}. They are both now aware of each other.',
                ref_players=werewolf_players)

        self.rendering_engine.render_game_statement('Werewolves, close your eyes.')

#Refais à neuf
    def night_seer(self):
        self.rendering_engine.render_game_statement(
            'Seer, wake up. You may look at another player’s card or two of the center cards.')
        seer_players = [player for player in self.players if player.card == 'Seer']
        if len(seer_players) == 0:
            self.rendering_engine.render_system_message('There are no seers in play.')
        else:
            self.rendering_engine.render_system_message(
                'There is one seer in play, {ref_players[0]}.'
                , ref_players=seer_players)
            self.rendering_engine.render_player_turn_init(seer_players[0])
            prompt = open('prompts/seer.txt').read()
            response = seer_players[0].run_prompt(prompt)
            global timerOn
            timerOn = datetime.datetime.now()
            if (seer_players[0].player_name.lower() == self.real_player_name.lower()):
                choice = input(f"Choose to know player role. Enter one of the following names {self.player_names}: ")
                while choice not in self.player_names:
                    choice = input(
                        f"Choose to know player role. Enter one of the following names {self.player_names}: ")
                reasoning = input("Enter the reason of your choice: ")
            else:
                action = return_dict_from_json_or_fix(response)
                reasoning = action['reasoning']
                choice = action['choice']
            if choice not in self.player_names:
                choice = random.choice(self.player_names)
            if (choice not in self.player_names):
                choice = random.choice(self.player_names)
            thoughts_message = f'NIGHT ROUND THOUGHTS: {reasoning}'
            seer_players[0].append_memory(thoughts_message)
            self.rendering_engine.render_player_turn(seer_players[0], None, reasoning)

            if choice == 'player':
                player_name = action['player']
                player = next((p for p in self.players if p.player_name == player_name), None)
                message = f'GAME (NIGHT PHASE): You are have seen that {player.player_name} has the card: {player.card}.'
                seer_players[0].append_memory(message)
                self.rendering_engine.render_system_message(
                    'The seer looked at a card from {ref_players[0]} and saw the card {ref_cards[0]}',
                    ref_players=[player], ref_cards=[player.card])
            else:
                viewed_cards = random.sample(self.middle_cards, k=1)
                message = f'GAME (NIGHT PHASE): You have seen two cards in the center of the table: {viewed_cards[0]} '
                seer_players[0].append_memory(message)
                self.rendering_engine.render_system_message(
                    'The seer looked at two cards from the center of the table and saw the cards {ref_cards[0]} and {ref_cards[1]}',
                    ref_cards=viewed_cards)
        self.rendering_engine.render_game_statement('Seer, close your eyes.')

#Refais à neuf également
    def day(self):
        self.rendering_engine.render_game_statement('Everyone, Wake up!')
        day_prompt = open('prompts/day.txt').read()
        pointer = -1
        discussion_count = 0
        target_player = None
        while discussion_count < self.discussion_depth:
            if target_player is None:
                pointer += 1
                if pointer > len(self.players) - 1:
                    pointer = 0
                player = self.players[pointer]
            else:
                try:
                    player = [player for player in self.players if player.player_name == target_player][0]
                    target_player = None
                except:
                    print()
                    print(
                        f'SYSTEM NOTE: The AI supplied {target_player} as the target player. To avoid a crash, we will skip this directed discussion.')
                    print()
            self.rendering_engine.render_player_turn_init(player)
            response = player.run_prompt(day_prompt)
            global timerOn
            timerOn = datetime.datetime.now()
            if (player.player_name.lower() == self.real_player_name.lower()):
                is_targeting = input(
                    "Would you like to say something directly to one of the players? Enter 'Yes' or 'No': ")
                if (is_targeting.lower() == 'yes'):
                    target_player = input(
                        f"To speak directly to player, enter one of the following names {self.player_names}: ")
                    while target_player not in self.player_names:
                        target_player = input(
                            f"To speak directly to player, enter one of the following names {self.player_names}: ")
                reasoning = input(f"Enter your reasoning: ")
                statement = input("Enter your statement: ")
            else:
                action = return_dict_from_json_or_fix(response)
                reasoning = action['reasoning']
                statement = action['statement']
                if 'target_player' in action:
                    target_player = action['target_player']
            thoughts_message = f'DAY ROUND THOUGHTS: {reasoning}'
            player.append_memory(thoughts_message)
            message = f'{player.player_name}: {statement}'
            for i_player in self.players:
                i_player.append_memory(message)
            self.rendering_engine.render_player_turn(player, statement, reasoning)
            discussion_count += 1

    def vote(self):
        self.rendering_engine.render_game_statement('It\'s time to vote!')
        vote_prompt = open('prompts/vote.txt').read()
        votes = {}
        for player in self.players:
            votes[player.player_name] = 0
        for player in self.players:
            self.rendering_engine.render_player_turn_init(player)
            response = player.run_prompt(vote_prompt)
            global timerOn
            timerOn = datetime.datetime.now()
            if (player.player_name.lower() == self.real_player_name.lower()):
                voted_player = input(
                    f"Vote to exclude the player. Enter one of the following names {self.player_names}: ")
                #while voted_player not in self.player_names:
                 #   voted_player = input(
                  #      f"Vote to exclude the player. Enter one of the following names {self.player_names}: ")
                reasoning = input("Enter the reason of your choice: ")
            else:
                action = return_dict_from_json_or_fix(response)
                reasoning = action['reasoning']
                voted_player = action['voted_player']
            if voted_player not in self.player_names:
                voted_player = random.choice(self.player_names)
            self.rendering_engine.render_player_vote(player, voted_player, reasoning)
            votes[voted_player] += 1
        self.rendering_engine.render_vote_results(votes, self.players)
        max_votes = max(votes.values())
        if max_votes == 1:
            werewolf_players = [player for player in self.players if player.card == 'Werewolf']
            if len(werewolf_players) == 0:
                game_result = 'No player was voted out. The villagers win.'
            else:
                game_result = 'No player was voted out. The werewolves win.'
        else:
            players_with_max_votes = [player for player in self.players if votes[player.player_name] == max_votes]
            if len(players_with_max_votes) > 1:
                game_result = f'There was a tie between {", ".join([player.player_name for player in players_with_max_votes])}.'
                if players_with_max_votes[0].card != 'Werewolf' and players_with_max_votes[1].card != 'Werewolf':
                    game_result += ' The werewolves win.'
                else:
                    game_result += ' The villagers win.'
            else:
                killed_player = players_with_max_votes[0]
                game_result = f'{killed_player.player_name} was killed.'
                if killed_player.card == 'Werewolf':
                    game_result += ' The villagers win.'
                else:
                    game_result += ' The werewolves win.'

        self.rendering_engine.render_game_statement(game_result)

    def get_player_names(self, player_count):
        name_options = ['Kassoum', 'Alexia', 'Andrei', 'Cristina', 'Dragos', 'Dracula', 'Carel', 'Ileana', 'Kraven',
                        'Larisa', 'Lucian', 'Marius', 'Michael', 'Mircea', 'Radu', 'Anas', 'Selene', 'Stefan',
                        'Viktor', 'Vladimir']
        if (self.real_player_name != ""):
            names_message = random.sample(name_options, player_count-1)
            names_message.append(self.real_player_name)
            while (len(names_message) != len(set(names_message))):
                names_message = random.sample(name_options, player_count-1)
                names_message.append(self.real_player_name)
        else:
           names_message = random.sample(name_options, player_count)
        return names_message

    def get_other_players(self, player_number, player_names):
        return [name for i, name in enumerate(player_names, 1) if i != player_number]

def start_game(player_count, discussion_depth, real_player_name=""):
    # Suppression de l'interaction utilisateur dans la fonction
    game = Game(player_count=player_count, discussion_depth=discussion_depth, real_player_name=real_player_name)
    game.play()
    return game.rendering_engine.messages, game.rendering_engine.user_prompts

