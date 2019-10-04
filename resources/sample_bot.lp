# Space Invaders Example Bot
# Name: Defender
#       ^^^^^^^^-- your name here!
#
# There are several variables provided for your convenience, described
# below.
#
# GAME ITEMS
#
# Here are all the possible things that are in a space:
# * MOTHERSHIP_L, MOTHERSHIP_C, MOTHERSHIP_R
# * INVADER_0, INVADER_1, INVADER_2
# * PLAYER_L, PLAYER_C, PLAYER_R
# * BARRIER_1, BARRIER_2, BARRIER_3, BARRIER_4 
# * MISSILE (alien projectiles)
# * BULLET (player projectiles)
# * EMPTY (nothing is in this space)
# 
# Note that the player and mothership are both three sapces wide, so
# they have a left, center, and right location. For the barriers and
# invaders, the different numbers correspond to the strength of the
# barrier space and the different classes of invader. Invader type does
# not affect gameplay.
#
# SENSORS
#
# Your bot is also provided some basic "sensors" in the form of
# variables that automatically contain values to tell you about the game
# state.
# * The variables player_left_minus_one, player_left, player_center,
#   player_right, and player_right_plus_one contain first item that is
#   directly above the three player spaces, as well as what is directly
#   above the player one space to either direction. If the
#   "left_minus_one" and "right_plus_one" spaces are off the game
#   board, the will be set to OUT_OF_BOUNDS.
# * bonus_ship_x will contain the x position of the center of the
#   mothership if it exists, otherwise this variable will contain the
#   value -1
# * player_x provides the player's x position (the center of the player)
#
# GAME MAP
# * map_array contains the entire map as a two dimensional array
#   (example of this being used at the bottom of the sample bot)
#   The variables MAP_WIDTH and MAP_HEIGHT contain the map width and
#   height.
# 


# This is a basic bot that moves randomly and tries to blast holes holes
# in barriers.

a = rand % 4

if a is 0 {
    move = west
}

if a is 1 {
    move = east
}

if a is 2 {
    move = fire
}

if a is 3 {
    move = stay
}

if player_center is BARRIER_4 or player_center is BARRIER_3 or player_center is BARRIER_2 or player_center is BARRIER_1 {
    move = fire
}

# example of accessing the map
# x = 0
# y = 0
# invaders_left = 0
# for x = 0; x < MAP_WIDTH; x = x + 1 {
#     for y = 0; y < MAP_HEIGHT; y = y + 1 {
#         thing = map_array[x][y]
#         if thing is INVADER_1 or thing is INVADER_2 or thing is INVADER_3 or thing is MOTHERSHIP_C {
#             invaders_left = invaders_left + 1
#         }
#     }
# }
