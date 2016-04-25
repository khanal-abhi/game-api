# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""

import endpoints
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from protorpc import remote, messages, message_types

from models import StringMessage, NewGameForm, GameForm, MakeMoveForm, \
    ScoreForms, GameForms, RankingForm, RankingForms, MoveForms, Move
from models import User, Game, Score, Card
from utils import get_by_urlsafe

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1), )
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1), )
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))

GET_USER_GAMES_REQUEST = endpoints.ResourceContainer(
    urlsafe_user_key=messages.StringField(1))

GET_HIGH_SCORES = endpoints.ResourceContainer(
    number_of_results=messages.StringField(1))

MEMCACHE_MOVES = 'MOVES_REMAINING'


@endpoints.api(name='concentration_game', version='v1')
class ConcentrationAPI(remote.Service):
    """Game API"""

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
            request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        try:
            game = Game.new_game(user.key)
        except ValueError:
            raise endpoints.BadRequestException('Maximum must be greater '
                                                'than minimum!')

        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        taskqueue.add(url='/tasks/cache_average_attempts')
        return game.to_form('Good luck playing Guess a Number!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message. The two
        positions are a and b"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.to_form('Game already over!')

        cards = Card.query(Card.game == game.key, Card.matched == False)
        position1 = request.a
        position2 = request.b

        unmatched_cards = []
        for card in cards:
            unmatched_cards.append(card)

        unmatched_cards_count = len(unmatched_cards)
        if unmatched_cards_count < 2:
            raise IndexError('No unmatched pair found but the game is not '
                             'over')

        cards_list = []
        msg = 'Boo'

        game.attempts += 1
        move = Move()
        move.card1 = position1
        move.card2 = position2
        move.game = game.key
        move.result = msg

        for card in unmatched_cards:
            if card.position == position1 or card.position == position2:
                cards_list.append(card)

        try:
            if cards_list[0].matched or cards_list[1].matched:
                move.result = 'Card alreadt matched'
                move.put()
                return game.to_form('Card already matched')

        except:
            msg = 'One of the cards is already matched. Please Try again.'
            move.result = msg
            move.put()
            return game.to_form(msg)

        if cards_list[0].value == cards_list[1].value:
            cards_list[0].matched = cards_list[1].matched = True
            cards_list[0].put()
            cards_list[1].put()
            msg = 'Yay'
            move.result = msg
            if unmatched_cards_count == 2:
                game.game_over = True
                game.end_game()
                msg = 'You win, Game Over'
                move.put()
                return game.to_form(msg)

        game.put()

        move.put()
        return game.to_form(msg)

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(response_message=StringMessage,
                      path='games/average_attempts',
                      name='get_average_attempts',
                      http_method='GET')
    def get_average_attempts(self, request):
        """Get the cached average moves"""
        return StringMessage(
            message=memcache.get(MEMCACHE_MOVES) or '')

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='games/get_user_games',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Get all active games for a given user."""
        user_name = request.user_name
        users = User.query(User.name == user_name)
        user = None
        for one_user in users:
            user = one_user
            break

        if user is None:
            return GameForms(games=[])

        games = Game.query(Game.user == user.key, Game.game_over == False,
                           Game.active == True)
        games_list = []
        for game in games:
            games_list.append(game.to_form('A game of concentration!'))

        return GameForms(games=games_list)

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='games/cancel_game',
                      name='cancel_game',
                      http_method='PUT')
    def cancel_game(self, request):
        """Cancels a game in progress"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        msg = 'Game cancelled'
        if game is not None:
            if game.active is False:
                msg = 'Game already cancelled'
            else:
                if game.game_over is True:
                    msg = 'Cannot cancel a completed game'
                else:
                    game.active = False
                    game.put()
                    msg = 'Game cancelled'

        return game.to_form(msg)

    @endpoints.method(request_message=GET_HIGH_SCORES,
                      response_message=ScoreForms,
                      path='games/get_high_scores',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        """Get the high scores with an option of a limit"""
        limit = request.number_of_results

        scores = Score.query().order(-Score.attempts)
        scores_list = []

        counter = 0

        for i in range(limit or len(scores)):
            scores_list.append(scores[i].to_form())

        return ScoreForms(items=scores_list)

    @endpoints.method(message_types.VoidMessage,
                      response_message=RankingForms,
                      path='games/get_user_rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Get user rankings"""
        users = User.query()
        attempts_count = 0
        attempts_total = 0
        rankings = []

        for user in users:
            scores = Score.query(Score.user == user.key)
            for score in scores:
                attempts_total += score.attempts
                attempts_count += 1.0

            if attempts_count != 0:
                average_attempts = attempts_total / attempts_count
            else:
                average_attempts = attempts_total / 1.0

            rankings.append(RankingForm(user_name=user.name,
                                        average_attempts=average_attempts))

            attempts_total = 0
            attempts_count = 0

        return RankingForms(items=rankings)

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=MoveForms,
                      path='games/get_game_history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """get moves history for each game requested"""
        url_safe_key = request.urlsafe_game_key
        game = get_by_urlsafe(url_safe_key, Game)
        moves = Move.query(Move.game == game.key)
        moves_list = []
        for move in moves:
            moves_list.append(move.to_form())

        return MoveForms(items=moves_list)

    @staticmethod
    def _cache_average_attempts():
        """Populates memcache with the average moves of Games"""
        games = Game.query(Game.game_over == True).fetch()
        if games:
            count = len(games)
            total_attempts = sum([game.attempts_remaining
                                  for game in games])
            average = float(total_attempts) / count
            memcache.set(MEMCACHE_MOVES,
                         'The average moves is {:.2f}'.format(
                             average))


api = endpoints.api_server([ConcentrationAPI])
