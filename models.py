"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

from datetime import date
from datetime import datetime
from google.appengine.ext import ndb
from protorpc import messages, message_types

import random


class CardForm(messages.Message):
    position = messages.IntegerField(1, required=True)
    value = messages.IntegerField(2, required=True)
    matched = messages.BooleanField(3, required=True)


class BoardForm(messages.Message):
    items = messages.MessageField(CardForm, 1, repeated=True)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    attempts = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    active = messages.BooleanField(4, required=True)
    message = messages.StringField(5, required=True)
    user_name = messages.StringField(6, required=True)
    board = messages.MessageField(BoardForm, 7, required=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    a = messages.IntegerField(1, required=True)
    b = messages.IntegerField(2, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = message_types.DateTimeField(2, required=True)
    attempts = messages.IntegerField(4, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)


class GameForms(messages.Message):
    """Return multiple GameForms"""
    games = messages.MessageField(GameForm, 1, repeated=True)


class RankingForm(messages.Message):
    """Return a Ranking"""
    user_name = messages.StringField(1, required=True)
    average_attempts = messages.FloatField(2, required=True)


class RankingForms(messages.Message):
    """Return all the rankings"""
    items = messages.MessageField(RankingForm, 1, repeated=True)


class MoveForm(messages.Message):
    """Return a Move"""
    card1 = messages.IntegerField(1, required=True)
    card2 = messages.IntegerField(2, required=True)
    result = messages.StringField(3, required=True)
    move_time = message_types.DateTimeField(4, required=True)
    game_key = messages.StringField(5, required=True)


class MoveForms(messages.Message):
    """Return all the moves for a game"""
    items = messages.MessageField(MoveForm, 1, repeated=True)


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()


class Card(ndb.Model):
    """Card object"""
    game = ndb.KeyProperty(required=True, kind='Game')
    value = ndb.IntegerProperty(required=True)
    position = ndb.IntegerProperty(required=True)
    matched = ndb.BooleanProperty(required=True, default=False)

    def to_form(self):
        form = CardForm()
        form.position = self.position
        if self.matched:
            form.value = self.value
        else:
            form.value = 99
        form.matched = self.matched
        return form


class Move(ndb.Model):
    """Move object with card1, card2, result, move_time, game"""
    card1 = ndb.IntegerProperty(required=True)
    card2 = ndb.IntegerProperty(required=True)
    result = ndb.StringProperty(required=True)
    move_time = ndb.DateTimeProperty(required=True, auto_now_add=True)
    game = ndb.KeyProperty(required=True, kind='Game')

    def to_form(self):
        form = MoveForm()
        form.card1 = self.card1
        form.card2 = self.card2
        form.result = self.result
        form.move_time = self.move_time
        form.game_key = self.game
        return form


class Game(ndb.Model):
    """Game object"""
    attempts = ndb.IntegerProperty(required=True, default=0)
    game_over = ndb.BooleanProperty(required=True, default=False)
    active = ndb.BooleanProperty(required=True, default=True)
    last_played = ndb.DateTimeProperty(auto_now_add=True)
    user = ndb.KeyProperty(required=True, kind='User')

    @classmethod
    def new_game(cls, user):
        """Creates and returns a new game"""
        game = Game(user=user,
                    game_over=False)
        game_key = game.put()
        cards = []
        for x in xrange(2):
            for y in xrange(10):
                cards.append(Card(value=y))

        random.shuffle(cards)
        for card in cards:
            card.position = cards.index(card)
            card.game = game_key
            card.put()

        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.attempts = self.attempts
        form.game_over = self.game_over
        form.active = self.active
        form.message = message

        cards = Card.query(Card.game == self.key)
        cards_list = []

        for card in cards:
            cards_list.append(card.to_form())

        form.board = BoardForm(items=cards_list)

        return form

    def end_game(self):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.put()
        # Add the game to the score 'board'
        score = Score(user=self.user, date=date.today(),
                      attempts=self.attempts)
        score.put()


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True, auto_now_add=True)
    attempts = ndb.IntegerProperty(required=True)

    def to_form(self):
        form = ScoreForm()
        form.user_name = self.user.get().name
        form.attempts = self.attempts
        form.date = datetime.combine(self.date, datetime.min.time())
        return form
