from __future__ import print_function, division
import math
from enum import Enum

import os
import sys  # for printing to stderr

from CYLGame import GameLanguage
from CYLGame import GridGame
from CYLGame import MessagePanel
from CYLGame import MapPanel
from CYLGame import StatusPanel
from CYLGame import PanelBorder
from CYLGame.Game import ConstMapping
from CYLGame.Player import DefaultGridPlayer
from resources.Invader import Invader


class Direction(Enum):
    RIGHT = 1
    LEFT = 2


class Breakout(GridGame):
    MAP_WIDTH = 35
    MAP_HEIGHT = 26
    SCREEN_WIDTH = MAP_WIDTH
    SCREEN_HEIGHT = MAP_HEIGHT + 6
    MSG_START = 20
    MAX_MSG_LEN = SCREEN_WIDTH - MSG_START - 1
    CHAR_WIDTH = 16
    CHAR_HEIGHT = 16
    GAME_TITLE = "Breakout"
    CHAR_SET = "resources/terminal16x16_gs_ro.png"
    MAX_TURNS = 900

    score = 0

    RED_POINTS = 25
    YELLOW_POINTS = 20
    ORANGE_POINTS = 15
    GREEN_POINTS = 10
    BLUE_POINTS = 5

    RED = chr(240)  # worth 50 points
    ORANGE = chr(241)  # worth 40 points
    YELLOW = chr(242)  # worth 30 points
    GREEN = chr(243)  # worth 30 points
    BLUE = chr(244)  # worth 30 points
    PLAYER = chr(245)
    WALL = chr(246)
    EMPTY = ' '
    ROBOT = chr(64)

    fire_rate = 2  # the fire rate of invaders

    def __init__(self, random):

        if (self.MAP_WIDTH - 2) % 3:
            print("Screen width not compatible with three-wide bricks.")
            sys.exit(1)
            
        self.random = random
        self.running = True
        self.centerx = self.MAP_WIDTH // 2
        self.centery = self.MAP_HEIGHT // 2
        self.player_pos = [self.centerx, (int)(self.MAP_HEIGHT * .99)]
        self.player_right = [self.centerx + 1, (int)(self.MAP_HEIGHT * .99)]
        self.player_rightright = [self.centerx + 2, (int)(self.MAP_HEIGHT * .99)]
        self.player_left = [self.centerx - 1, (int)(self.MAP_HEIGHT * .99)]
        self.player_leftleft = [self.centerx - 2, (int)(self.MAP_HEIGHT * .99)]
        self.ball_pos = [self.centerx, self.MAP_HEIGHT - 2]
        self.ball_xchg = 1
        self.ball_ychg = -1
        self.ball_delay = 1
        self.saved_tile = self.EMPTY
        self.invaders = []
        self.invaders_left = 0
        self.turns = 0
        self.level = 0
        self.level_bonus = 5
        self.bricks_left = 0
        self.msg_panel = MessagePanel(self.MSG_START, self.MAP_HEIGHT + 1, self.SCREEN_WIDTH - self.MSG_START, 5)
        self.status_panel = StatusPanel(0, self.MAP_HEIGHT + 1, self.MSG_START, 5)
        self.panels = [self.msg_panel, self.status_panel]
        self.msg_panel.add(self.GAME_TITLE)
        self.lives = 3
        self.life_lost = False

        self.debug = False

    def init_board(self):
        self.map = MapPanel(0, 0, self.MAP_WIDTH, self.MAP_HEIGHT, self.EMPTY,
                            border=PanelBorder.create(bottom="-"))
        self.panels += [self.map]

        self.draw_level()

    def start_game(self):
        # This is a hack to make sure that the map array is setup before the player makes their first move.
        self.player.bot_vars = self.get_vars_for_bot()

    def create_new_player(self, prog):
        self.player = DefaultGridPlayer(prog, self.get_move_consts())
        return self.player

        
    def draw_level(self):
        if self.debug:
            print("Redrawing map! turn: %d" % (self.turns))

        # clear the existing map (in case of level reset)
        for w in range(0, self.MAP_WIDTH):
            for h in range(0, self.MAP_HEIGHT):
                self.map[(w,h)] = self.EMPTY

        # reset player/ball positions in case of reset
        self.player_pos = [self.centerx, (int)(self.MAP_HEIGHT * .99)]
        self.player_right = [self.centerx + 1, (int)(self.MAP_HEIGHT * .99)]
        self.player_rightright = [self.centerx + 2, (int)(self.MAP_HEIGHT * .99)]
        self.player_left = [self.centerx - 1, (int)(self.MAP_HEIGHT * .99)]
        self.player_leftleft = [self.centerx - 2, (int)(self.MAP_HEIGHT * .99)]
        self.ball_pos = [self.centerx, self.MAP_HEIGHT - 2]


        # draw ball
        self.map[(self.ball_pos[0], self.ball_pos[1])] = self.ROBOT

        # draw player
        self.map[(self.player_pos[0], self.player_pos[1])] = self.PLAYER
        self.map[(self.player_right[0], self.player_right[1])] = self.PLAYER
        self.map[(self.player_rightright[0], self.player_rightright[1])] = self.PLAYER
        self.map[(self.player_left[0], self.player_left[1])] = self.PLAYER
        self.map[(self.player_leftleft[0], self.player_leftleft[1])] = self.PLAYER

        # make outer walls
        # top bar
        for w in range(0, self.MAP_WIDTH):
            self.map[(w, 0)] = self.WALL

        # sides
        for h in range(0, self.MAP_HEIGHT):
            self.map[(0, h)] = self.WALL
            self.map[(self.MAP_WIDTH -1, h)] = self.WALL

        # generate barriers
        for w in range(1, self.MAP_WIDTH - 1):
            for h in range(5, 10):
                self.bricks_left = self.bricks_left + 1
                if h == 5: self.map[(w, h)] = self.RED
                elif h == 6: self.map[(w, h)] = self.ORANGE
                elif h == 7: self.map[(w, h)] = self.YELLOW
                elif h == 8: self.map[(w, h)] = self.GREEN
                elif h == 9: self.map[(w, h)] = self.BLUE

    def is_brick(self, tile):
        if tile == self.RED or tile == self.ORANGE or tile == self.YELLOW or tile == self.GREEN or tile == self.BLUE:
            return True
        return False

    def get_line(start, end):
        """Bresenham's Line Algorithm produces a list of tuples from 
        start and end
        >>> points1 = get_line((0, 0), (3, 4))
        >>> points2 = get_line((3, 4), (0, 0))
        >>> assert(set(points1) == set(points2))
        >>> print points1
        [(0, 0), (1, 1), (1, 2), (2, 3), (3, 4)]
        >>> print points2
        [(3, 4), (2, 3), (1, 2), (1, 1), (0, 0)]
        """
        # Stolen shamelessly (ok, a little shamefully, but not very much) from:
        # http://www.roguebasin.com/index.php?title=Bresenham%27s_Line_Algorithm#Python
        # (this is a public source of algorithms for programmers)
        
        # Setup initial conditions
        x1, y1 = start
        x2, y2 = end
        dx = x2 - x1
        dy = y2 - y1
     
        # Determine how steep the line is
        is_steep = abs(dy) > abs(dx)
     
        # Rotate line
        if is_steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
     
        # Swap start and end points if necessary and store swap state
        swapped = False
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            swapped = True
     
        # Recalculate differentials
        dx = x2 - x1
        dy = y2 - y1
     
        # Calculate error
        error = int(dx / 2.0)
        ystep = 1 if y1 < y2 else -1
     
        # Iterate over bounding box generating points between start and end
        y = y1
        points = []
        for x in range(x1, x2 + 1):
            coord = (y, x) if is_steep else (x, y)
            points.append(coord)
            error -= abs(dy)
            if error < 0:
                y += ystep
                error += dx
     
        # Reverse the list if the coordinates were swapped
        if swapped:
            points.reverse()
        return points

    def move_robot(self):

        if self.turns % self.ball_delay == 0:
            # erase the robot from its current position
            self.map[(self.ball_pos[0], self.ball_pos[1])] = self.EMPTY

            # bounce off a horizontal surface
            if (self.ball_pos[1] == 1 and self.ball_ychg) == -1 or (self.ball_pos[1] == self.MAP_HEIGHT - 2 and self.ball_ychg == 1 and self.ball_pos[0] >= self.player_leftleft[0] and self.ball_pos[0] <= self.player_rightright[0]):
                self.ball_ychg = self.ball_ychg * -1
            
            # bounce off a vertical surface
            if (self.ball_pos[0] == 1 and self.ball_xchg == -1) or (self.ball_pos[0] == self.MAP_WIDTH -2 and self.ball_xchg == 1):
                self.ball_xchg = self.ball_xchg * -1

            # move robot based on angle and direction
            self.ball_pos[1] = self.ball_pos[1] + self.ball_ychg
            self.ball_pos[0] = self.ball_pos[0] + self.ball_xchg
            
            # before we overwrite robot's new position, save the map
            # contents to a temp variable -- we'll use this to check for
            # a collision with a barrier, change dir and assign points.
            self.saved_tile = self.map[(self.ball_pos[0], self.ball_pos[1])]
            
            if self.is_brick(self.saved_tile):

                self.bricks_left = self.bricks_left - 1
                if self.debug: print("Hit! Bricks left: %d" % (self.bricks_left))

                # add the appropriate score
                if self.saved_tile == self.RED:
                    self.score = self.score + self.RED_POINTS + self.level * self.level_bonus
                elif self.saved_tile == self.ORANGE:
                    self.score = self.score + self.ORANGE_POINTS + self.level * self.level_bonus
                elif self.saved_tile == self.YELLOW:
                    self.score = self.score + self.YELLOW_POINTS + self.level * self.level_bonus
                elif self.saved_tile == self.GREEN:
                    self.score = self.score + self.GREEN_POINTS + self.level * self.level_bonus
                elif self.saved_tile == self.BLUE:
                    self.score = self.score + self.BLUE_POINTS + self.level * self.level_bonus

                # identify and clear the brick in question
                # bricks are three tiles wide and the robot can hit any
                # tile in the brick and the whole thing must clear.
                x_off = self.ball_pos[0] - 1
                brick_num = int(x_off / 3) # bricks start at 0 on left

                # clear complete brick
                self.map[((brick_num * 3) + 1, self.ball_pos[1])] = self.EMPTY
                self.map[((brick_num * 3) + 2, self.ball_pos[1])] = self.EMPTY
                self.map[((brick_num * 3) + 3, self.ball_pos[1])] = self.EMPTY

                # change direction / angle of robot
                self.ball_ychg = self.ball_ychg * -1

            # redraw the robot in its new position
            self.map[(self.ball_pos[0], self.ball_pos[1])] = self.ROBOT

        return

    def do_turn(self):
        self.handle_key(self.player.move)
        self.player.bot_vars = self.get_vars_for_bot()
        # End of the game
        if self.turns >= self.MAX_TURNS:
            self.running = False
            self.msg_panel.add("You are out of moves.")
        if self.lives == 0:
            self.running = False
            msg = "You lost all your lives"
            self.msg_panel.add(msg)
            if self.debug:
                print(msg)
        if self.life_lost:
            self.life_lost = False
            msg = "You lost a life"
            self.map[(self.ball_pos[0], self.ball_pos[1])] = self.EMPTY
            self.msg_panel.add(msg)
            if self.debug:
                print(msg)


    def handle_key(self, key):
        self.turns += 1

        self.map[(self.player_pos[0], self.player_pos[1])] = self.EMPTY
        self.map[(self.player_right[0], self.player_pos[1])] = self.EMPTY
        self.map[(self.player_rightright[0], self.player_pos[1])] = self.EMPTY
        self.map[(self.player_left[0], self.player_pos[1])] = self.EMPTY
        self.map[(self.player_leftleft[0], self.player_pos[1])] = self.EMPTY
        # if key == "w":
        # self.player_pos[1] -= 1
        # if key == "s":
        # self.player_pos[1] += 1
        if key == "a":
            if self.player_leftleft[0] - 1 >= 1:
                self.player_left[0] -= 1
                self.player_leftleft[0] -= 1
                self.player_pos[0] -= 1
                self.player_right[0] -= 1
                self.player_rightright[0] -= 1
        if key == "d":
            if self.player_rightright[0] + 1 < self.MAP_WIDTH - 1:
                self.player_pos[0] += 1
                self.player_right[0] += 1
                self.player_rightright[0] += 1
                self.player_left[0] += 1
                self.player_leftleft[0] += 1
        if key == "Q":
            self.running = False
            return

        # move the robot

        self.move_robot()  # we do hits detection first
        
        if self.bricks_left == 0:
            self.level += 1
            if self.ball_delay > 1:
                self.ball_delay = self.ball_delay - 1

            if self.debug:
                print("*************************************************")
                print("No more bricks! New level: %d" % self.level)
                print("*************************************************")

            self.draw_level()
            return

# put the ball bouncing off the paddle here
        # collision detection
#        position = self.map[(self.player_pos[0], self.player_pos[1])]
#        position_left = self.map[(self.player_left[0], self.player_left[1])]
#        position_right = self.map[(self.player_right[0], self.player_right[1])]
#
#        collision = False
#        if position == self.MISSILE or position == self.INVADER2 or position == self.INVADER1 or position == self.INVADER0:
#            collision = True
#        if position_left == self.MISSILE or position == self.INVADER2 or position == self.INVADER1 or position == self.INVADER0:
#            collision = True
#        if position_right == self.MISSILE or position == self.INVADER2 or position == self.INVADER1 or position == self.INVADER0:
#            collision = True

        # self.msg_panel.remove("You lost a life!")
        if self.ball_pos[1] == self.MAP_HEIGHT - 1:
            if self.debug:
                print("You lost a life!")
            self.msg_panel.add(["You lost a life!"])
            self.lives -= 1
            
            # get new starting point
            new_center = self.random.randint(3, self.MAP_WIDTH - 3)
           

            # reset to center
            self.player_pos = [new_center, (int)(self.MAP_HEIGHT * .99)]
            self.player_right = [new_center + 1, (int)(self.MAP_HEIGHT * .99)]
            self.player_rightright = [new_center + 2, (int)(self.MAP_HEIGHT * .99)]
            self.player_left = [new_center - 1, (int)(self.MAP_HEIGHT * .99)]
            self.player_leftleft = [new_center - 2, (int)(self.MAP_HEIGHT * .99)]

            # ball_pos reset
            self.map[(self.ball_pos[0], self.ball_pos[1])] = self.EMPTY
            self.ball_pos = [new_center, self.MAP_HEIGHT - 2]
            self.map[(self.ball_pos[0], self.ball_pos[1])] = self.ROBOT

        # redraw player
        self.map[(self.player_pos[0], self.player_pos[1])] = self.PLAYER
        self.map[(self.player_left[0], self.player_pos[1])] = self.PLAYER
        self.map[(self.player_leftleft[0], self.player_pos[1])] = self.PLAYER
        self.map[(self.player_right[0], self.player_pos[1])] = self.PLAYER
        self.map[(self.player_rightright[0], self.player_pos[1])] = self.PLAYER

        # redraw ball
        self.map[(self.ball_pos[0], self.ball_pos[1])]
        
        # first we clear all the prevoius invaders
#        for old_invader in self.map.get_all_pos(self.INVADER2):
#            self.map[old_invader] = self.EMPTY
#        for old_invader in self.map.get_all_pos(self.INVADER1):
#            self.map[old_invader] = self.EMPTY
#        for old_invader in self.map.get_all_pos(self.INVADER0):
#            self.map[old_invader] = self.EMPTY
#
    def is_running(self):
        return self.running

    def get_vars_for_bot(self):
        bot_vars = {}

        # player x location (center)

        player_x = self.player_pos[0]
        bot_vars["player_x"] = player_x
        bot_vars["ball_x"] = self.ball_pos[0]
        bot_vars["ball_y"] = self.ball_pos[1]
        bot_vars["lives"] = self.lives
        bot_vars["bricks_left"] = self.bricks_left

        bot_vars["map_array"] = self.get_map_array_tuple()

        # TODO: pass in the map to the bot

        return bot_vars

    def get_map_array_tuple(self):
        map_arr = []
        for w in range(0, self.MAP_WIDTH):
            w_arr = []
            for h in range(0, self.MAP_HEIGHT):
                w_arr.append(ord(self.map.p_to_char[(w, h)]))
            map_arr.append(tuple(w_arr))

        return tuple(map_arr)

    @staticmethod
    def default_prog_for_bot(language):
        if language == GameLanguage.LITTLEPY:
            return open(os.path.join(os.path.dirname(__file__), "resources/sample_bot.lp"), "r").read()

    @staticmethod
    def get_intro():
        return open(os.path.join(os.path.dirname(__file__), "resources/intro.md"), "r").read()
        # return "Welcome to Space Invaders"

    def get_score(self):
        return self.score

    def draw_screen(self, frame_buffer):
        # if not self.running:
        # self.msg_panel += [""+str(self.drops_eaten)+" drops. Good job!"]

        # Update Status
        self.status_panel["Invaders"] = len(self.invaders)
        self.status_panel["Lives"] = str(self.lives)
        self.status_panel["Move"] = str(self.turns) + " of " + str(self.MAX_TURNS)
        self.status_panel["Score"] = str(self.score)

        for panel in self.panels:
            panel.redraw(frame_buffer)

    @staticmethod
    def get_move_consts():
        return ConstMapping({"west": ord("a"),
                             "east": ord("d"),
                             "fire": ord("w"),
                             "stay": ord("s"),
                             "RED": ord(Breakout.RED),
                             "ORANGE": ord(Breakout.ORANGE),
                             "YELLOW": ord(Breakout.YELLOW),
                             "GREEN": ord(Breakout.GREEN),
                             "BLUE": ord(Breakout.BLUE),
                             "WALL": ord(Breakout.WALL),
                             "ROBOT": ord(Breakout.ROBOT),
                             "PLAYER": ord(Breakout.PLAYER),
                             "EMPTY": ord(' '),
                             "MAP_HEIGHT": Breakout.MAP_HEIGHT,
                             "MAP_WIDTH": Breakout.MAP_WIDTH,
                             })


if __name__ == '__main__':
    from CYLGame import run

    run(Breakout)
