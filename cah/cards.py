from .util import card
import warnings
warnings.simplefilter("once")
import random
import os


ANSWERS_LOCATION = 'data/bin/answer.txt'
QUESTIONS_LOCATION = 'data/bin/question.txt'


def get_data(file_name):
    data = []
    with open(os.path.join(os.path.dirname(__file__), file_name)) as a_file:
        for ln in a_file:
            ln = ln.rstrip('\n')
            data.extend(card.from_str(ln))

    return data


def filter_multi_blanks(arr):
    for i in reversed(range(len(arr))):
        s = arr[i]
        inside = False
        count = 0
        for c in s:
            if c == '_':
                if not inside:
                    count += 1
                    inside = True
            else:
                inside = False
        if count > 1:
            del(arr[i])

    return arr

questions = filter_multi_blanks(get_data(QUESTIONS_LOCATION))
answers = get_data(ANSWERS_LOCATION)


def load_cards(loc):
    try:
        return get_data(loc)
    except FileNotFoundError:
        warnings.warn("Card data not available.", ResourceWarning)
        return []




class CardGroup:
    def __init__(self, card_arr):
        self.cards = {}
        self.used_cards = {}

        for idx, crd in enumerate(card_arr):
            self.cards[idx] = crd

    def get_new_card_by_id(self, card_id):
        crd = self.cards[card_id]
        del(self.cards[card_id])
        self.used_cards[card_id] = crd
        return crd

    def get_new_card_random(self):
        card_id = random.choice(list(self.cards.keys()))
        return card_id, self.get_new_card_by_id(card_id)

    def get_card_by_id(self, card_id):
        try:
            return self.cards[card_id]
        except KeyError:
            return self.used_cards[card_id]

    def card_used(self, card_id):
        if card_id in self.cards:
            return False
        elif card_id in self.used_cards:
            return True
        else:
            raise KeyError("Given card ID not found.")
