from .util import card
import warnings
warnings.simplefilter("once")
import random
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np


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


def break_fix(text, width, draw, font):
    if not text:
        return
    lo = 0
    hi = len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        t = text[:mid]
        w, h = draw.textsize(t,font=font)
        if w <= width:
            lo = mid
        else:
            hi = mid - 1
    t = text[:lo]
    w, h = draw.textsize(t, font=font)
    yield t, w, h
    yield from break_fix(text[lo:], width, draw, font)


def fit_text(img, text, color, font):
    width = img.size[0] - 2
    draw = ImageDraw.Draw(img)
    pieces = list(break_fix(text, width-23, draw, font))
    height = sum(p[2] for p in pieces)
    if height > img.size[1]:
        raise ValueError("text doesn't fit")
    y = (img.size[1] - height) // 2
    for t, w, h in pieces:
        x = (img.size[0] - w) // 2
        draw.text((x, y), t, font=font, fill=color)
        y += h


def Card_To_Image(card_data: str, card_num: int):
    c_name = ''.join([i[0] for i in card_data.split()])

    logo = Image.open("cah/img/logo.png")  #logo
    logo.thumbnail((25, 25))
    card = Image.new("RGB", (180, 180), 'white') #card maker
    edit = ImageDraw.Draw(card)
    card_borders = [(170, 170, 10, 170), (170, 170, 170, 10), (10, 10, 170, 10), (10, 170, 10, 10)]
    for border in card_borders:
        edit.line(border, fill='black', width=3)
    font = ImageFont.truetype('cah/font/Montserrat.ttf', size=13)

    fit_text(card, card_data, (0, 0, 0), font=font)

    edit.text((85, 25), f'({card_num})', fill='black', font=font)
    
    card.paste(logo, (130, 130))
    #card.save('test.png')
    return card


def combine_cards(images: tuple):
    x_offset = 0

    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)
    max_height = max(heights)
    new_im = Image.new('RGB', (total_width, max_height))
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    return new_im


def deck_maker(deck: tuple):
    images = []
    for i, j in deck:
        images.append(Card_To_Image(card_data=j, card_num=i))

    cards = [combine_cards(tuple(images[:4])), combine_cards(tuple(images[4:]))]
    deck = Image.new('RGB', (720, 360))
    deck.paste(cards[0], (0, 0))
    deck.paste(cards[1], (0, 180))
    return deck
