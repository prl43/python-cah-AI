from . import cards, player


MAX_CARDS_PER_PLAYER = 8


class Game:
    def __init__(self):
        self.curr_question = None
        self.max_round = 15
        self.cur_round = 1
        self.win_pts = 5
        self.questions = cards.CardGroup(cards.questions)
        self.answers = cards.CardGroup(cards.answers)

        self.players = []

        self.host = None
        self.player_cards = {}
        self.card_tzar = None
        self.next_tzar = None
        self.finish_round = 0
        self.player_choices = []
        self.has_played = []

    def add_player(self, player_id):
        new_player = player.Player(player_id)
        self.players.append(new_player)
        return new_player

    def get_new_question(self):
        self.curr_question = self.questions.get_new_card_random()
        return self.curr_question

    def deal_cards(self):
        num_cards = len(self.answers.cards)

        deal_num = int(num_cards/len(self.players))

        if deal_num > MAX_CARDS_PER_PLAYER:
            deal_num = MAX_CARDS_PER_PLAYER
        elif deal_num < 1:
            raise KeyError("Not enough cards to continue play.")

        for p in self.players:
            while len(p.cards) < deal_num:
                new_card = self.answers.get_new_card_random()
                p.cards[new_card[0]] = new_card[1]

    def reset_player_cards(self):
        self.player_cards = {}

    def set_player_card(self, plyr, card_id):
        card_data = plyr.select_card(card_id)
        self.player_cards[plyr] = (card_id, card_data)
        return card_data

    def get_player_no_card(self):
        return [x for x in self.players if x not in self.player_cards.keys()]

    def set_round_winner(self, plyr):
        answer = self.player_cards[plyr]
        opponent_answers = [value for key, value in self.player_cards.items() if key not in [plyr]]
        #plyr.add_win(self.curr_question[0], answer, opponent_answers)
        plyr.add_win()

    def set_card_tzar(self, plyr):
        self.card_tzar = plyr
