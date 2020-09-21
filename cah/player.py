class Player:
    def __init__(self, player_id):
        self.cards = {}
        self.wins = 0
        self.id = player_id
        self.fake_id = None

    #def add_win(self, question, answer, opponent_answers):
        #self.wins[question] = {'answer': answer, 'opponent_answers': opponent_answers}
    def add_win(self):
        self.wins += 1

    def select_card(self, card_id):
        if card_id not in self.cards:
            raise KeyError("Card ID not in possession of this Player.")

        crd = self.cards.pop(card_id)
        return crd
