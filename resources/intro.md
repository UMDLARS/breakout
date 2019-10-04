# LARS' Space Invaders

## Introduction

Aliens are invading! Thankfully, a new model of autonomous drone, the MJ324B can be used to destroy alien ships without risking human life. However, it turns out the programmer in charge of the drone's behavior didn't do a very good job. As a result, the drones function horribly. In this simulation, which looks remarkably close to the old "space invaders" game, we are able to test drone logic without much physical risk. 

Your job is to write a program that is able to survive the invasion with the highest score. The fate of humanity lies in your hands. 

## The Default Program

## Map Elements and Constants
There are several elements that can be on the map at any time. These are:

`MOTHERSHIP_L`, `MOTHERSHIP_C`, `MOTHERSHIP_R`, `INVADER_0`, `INVADER_1`, `INVADER_2`, `BARRIER_1`, `BARRIER_2`, `BARRIER_3`, `BARRIER_4`, `MISSILE`, `BULLET`, `PLAYER_L`, `PLAYER_C`, `PLAYER_R`, `EMPTY`, `OUT_OF_BOUNDS`

Your bot will be provided all these variables, so you can do `if x is INVADER_0` or something similar.

You are also provided the map width and height in the `MAP_WIDTH` and `MAP_HEIGHT` variables

## Variables

You are provided several variables that update every turn. 
`player_left_minus_one`, `player_left`, `player_center`, `player_right`, and `player_right_plus_one` will tell you what is above the player, as well as what is directly above the player one space to either direction.

`bonus_ship_x` will contain the x position of the center of the bonus ship (aka the mothership) if it exists, otherwise this variable will contain the value -1
`player_x` provides the player's x position (the center of the player)

`map_array` will contain the entire map in a 2-d array

To move or fire you must set the variable `move` to `east`, `west`, or `fire`. To stay in place, set `move` to *any other value*, such as `stay`, or don't set `move` to anything.

## Hints
You can make some helper functions and loops in little python (see the little python documentation for more information). You can use these to make detecting barriers and aliens a little easier. 

