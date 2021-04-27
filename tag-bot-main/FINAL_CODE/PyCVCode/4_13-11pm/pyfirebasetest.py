import pyrebase
import time

config = {
  "apiKey": "AIzaSyBcuL2qDigb_3q9yu1UaHx7Sw8fpYI-fpU",
  "authDomain": "tag-bot-f4476.firebaseapp.com",
  "databaseURL": "https://tag-bot-f4476-default-rtdb.firebaseio.com/",
  "storageBucket": "tag-bot-f4476.appspot.com"
}

firebase = pyrebase.initialize_app(config)
while True:
    database = firebase.database()
    Game_Mode = str(database.child("TAG_Bot").child("Mode").get().val())
    Game_Mode = Game_Mode[1:len(Game_Mode) - 1]
    game_length_time = int(database.child("TAG_Bot").child("Time").get().val())
    game_difficulty = str(database.child("TAG_Bot").child("Difficulty").get().val())
    game_difficulty = game_difficulty[1:len(game_difficulty) - 1]

    print("Mode " + str(Game_Mode))
    print("Difficulty " + str(game_difficulty))
    print("time " + str(game_length_time))

    time.sleep(1)