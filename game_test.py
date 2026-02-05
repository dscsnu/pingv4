from pingv4 import RandomBot, MinimaxBot, GameConfig, Connect4Game

game = Connect4Game(MinimaxBot, MinimaxBot, GameConfig(bot_delay_seconds=0.5))
game.run()
