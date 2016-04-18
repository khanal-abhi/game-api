#Full Stack Nanodegree Project 4 Refresh

## Run Instruction:
1. Run the app for development purposes using dev_appserver.py .
2. Open chrome with argument --unsafely-treat-insecure-origin-as-secure
 so that we can test the endpoints that is being run via http while the 
 api explorer is on https.
 
 If using OS X, both the steps can be done by using the provided bash script 
 using the command `./osx_shell.sh`
 
3. browse to the address `localhost:8080/_ah/api/explorer`
4. Test the app.
 
 
##Game Description:
Concentration is a API based game that sets up a game with 20 cards (10 pairs or matching cards).
A new user can be created and a new game started and played until all 10 pairs are matched.
Many different Guess a Number games can be played by many different Users at any
given time. Each game can be retrieved or played by using the path parameter
`urlsafe_game_key`.

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not. 
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.
    
 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, a, b
    - Returns: GameForm with new game state.
    - Description: Accepts two parameters a and b which are the two positions
    of the cards that the user wants to see if matching.
    
 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).
    
 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms. 
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.
    
 - **get_active_game_count**
    - Path: 'games/active'
    - Method: GET
    - Parameters: None
    - Returns: StringMessage
    - Description: Gets the average number of attempts for all games
    from a previously cached memcache key.

##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.
    
 - **Card**
    - Records the value and position of each cards along with its state of 
    having been matched or not.
 
##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, attempts,
    game_over flag, message, user_name).
 - **NewGameForm**
    - Used to create a new game (user_name, a, b)
 - **MakeMoveForm**
    - Inbound make move form (guess).
 - **ScoreForm**
    - Representation of a completed game's Score (user_name, date, attempts).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **StringMessage**
    - General purpose String container.