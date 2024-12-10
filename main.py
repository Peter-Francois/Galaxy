# To modify the window size when pressing "run"
# (This configuration must be set before all imports)
from kivy.config import Config
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '550')

from kivy.uix.relativelayout import RelativeLayout
from kivy.lang import Builder
import random
from kivy import platform
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics import Color, Line, Quad, Triangle
from kivy.properties import NumericProperty, ObjectProperty, Clock, StringProperty
from kivy.core.audio import SoundLoader

Builder.load_file('menu.kv')

class MainWidget(RelativeLayout):
    # We import the functions contained in the Python files external to the main file
    from transforms import transform, transform_2D, transform_3D
    from user_actions import keyboard_closed, on_keyboard_down, on_keyboard_up, on_touch_down, on_touch_up
    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    V_NB_LINES = 8
    V_LINES_SPACING = .4
    verticals_lines = []

    H_NB_LINES = 8
    H_LINES_SPACING = .15
    horizontal_lines = []

    speed = 3
    current_offset_y = 0
    current_y_loop = 0

    speed_x = 20
    current_offset_x = 0
    current_speed_x = 0

    NB_TILES = 20
    tiles = []
    tiles_coordinates = []

    SHIP_WIDTH = .1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04
    ship = None
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]

    state_game_over = False
    state_game_has_started = False

    menu_title = StringProperty("G   A   L   A   X   Y")
    difficulty_label = StringProperty("DIFFICULTY LEVEL")
    menu_button_easy = StringProperty("EASY")
    menu_button_normal = StringProperty("NORMAL")
    menu_button_hard = StringProperty("HARD")

    score_txt = StringProperty('')

    sound_begin = None
    sound_galaxy = None
    sound_game_over_impact = None
    sound_game_over_voice = None
    sound_music1 = None
    sound_restart = None

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_audio()
        self.sound_galaxy.play()
        self.init_vertical_line()
        self.init_horizontal_line()
        self.init_tile()
        # Important to call init_ship after init_tile so that the ship is displayed on top of the path
        self.init_ship()
        self.reset_game("easy")

        # Configure the keyboard only when on a computer, otherwise the smartphone keyboard
        # will appear on the screen
        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)
        # To advance the game, we use the Clock function with our update
        Clock.schedule_interval(self.update, 1.0 / 60)

    def init_audio(self):
        self.sound_begin = SoundLoader.load('audio/begin.wav')
        self.sound_galaxy = SoundLoader.load('audio/galaxy.wav')
        self.sound_game_over_impact = SoundLoader.load('audio/gameover_impact.wav')
        self.sound_game_over_voice = SoundLoader.load('audio/gameover_voice.wav')
        self.sound_music1 = SoundLoader.load('audio/music1.wav')
        self.sound_restart = SoundLoader.load('audio/restart.wav')
        self.sound_music1.volume = 1
        self.sound_begin.volume = .25
        self.sound_galaxy.volume = .25
        self.sound_game_over_voice.volume = .25
        self.sound_restart.volume = .25
        self.sound_game_over_impact.volume = .6

        self.sound_music1.loop = True

    def reset_game(self, level):
        if level == "easy":
            self.speed = 4
        if level == "normal":
            self.speed = 5
        if level == "hard":
            self.speed = 6
        self.current_offset_y = 0
        self.current_y_loop = 0
        self.score_txt = f'SCORE: {self.current_y_loop}'
        self.current_offset_x = 0
        self.current_speed_x = 0
        self.tiles_coordinates = []

        self.pre_fill_tiles_coordinates()
        self.genegerate_tiles_coordinates()
        self.state_game_over = False

    def is_desktop(self):  # We need to check if we are on a computer or a smartphone
        if platform in ('linux', 'win', 'macosx'):
            return True
        else:
            return False

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def update_ship(self):
        center_x = self.width / 2
        base_y = self.SHIP_BASE_Y * self.height
        half_width = self.SHIP_WIDTH * self.width / 2
        height = self.SHIP_HEIGHT * self.height
        # We retrieve the coordinates of the ship before transformation to check for collisions
        self.ship_coordinates[0] = (center_x - half_width, base_y)
        self.ship_coordinates[1] = (center_x, base_y + height)
        self.ship_coordinates[2] = (center_x + half_width, base_y)
        # The * here allows us to read the values contained
        # in the tuple, not the tuple itself
        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])
        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def check_ship_collisions(self):
        for i in range (0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            # Exit condition for the loop to avoid iterating over all the ti_y values since the collision
            # can only occur with the first or second tile. If ti_y is strictly greater
            # than the coordinate of the second tile, we return False to stop looping
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    def check_ship_collision_with_tile(self, ti_x, ti_y):
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x+1, ti_y+1)
        for i in range(0, len(self.ship_coordinates)):
            px, py = self.ship_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                # The ship's point is inside the tile
                return True
        return False

    def init_tile(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.NB_TILES):
                self.tiles.append(Quad())

    def pre_fill_tiles_coordinates(self):
        for i in range(0, 10):
            self.tiles_coordinates.append((0, i))

    def genegerate_tiles_coordinates(self):
        last_y = 0
        last_x = 0
        start_index = -int(self.V_NB_LINES / 2) + 1
        end_index = start_index + self.V_NB_LINES - 1

        # The first -1 is to start from the end of tiles_coordinates towards the beginning to avoid index issues.
        # The second -1 is because we want to look at the value at index 0.
        # The third is to iterate in reverse order.
        for i in range(len(self.tiles_coordinates) - 1, -1, -1):
            # We check if a tile has its y-coordinate (index [1]) that is less than the number of loops we have made
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        # We need to remember the last coordinate in order to modify the value of last_y
        if len(self.tiles_coordinates) > 0:
            last_coordinate = self.tiles_coordinates[-1]
            last_x = last_coordinate[0]
            last_y = last_coordinate[1] + 1

        # The for loop starts from the size of tiles_coordinates, so when initializing, we create NB_TILES tiles,
        # and then we need to first remove the tile that is off the screen in order to recreate a new tile
        for i in range(len(self.tiles_coordinates), self.NB_TILES):
            # For the random playground generation:
            # 0 -> forward
            # 1 -> right
            # 2 -> left
            r = random.randint(0, 2)

            # To stay on the playing field
            if last_x <= start_index:
                r = 1
            if last_x >= end_index - 1:
                r = 2

            self.tiles_coordinates.append((last_x, last_y))
            if r == 1:
                last_x += 1  # right tile
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1  # Tile in front, after moving to the right
                self.tiles_coordinates.append((last_x, last_y))
            elif r == 2:
                last_x -= 1  # left tile
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1  # tile in front, after moving to the left
                self.tiles_coordinates.append((last_x, last_y))
            # Increment last_y for the next series
            last_y += 1

    def init_vertical_line(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.V_NB_LINES):
                self.verticals_lines.append(Line())

    # The functions get_line_x_from_index and get_line_y_from_index were created to more easily
    # retrieve the coordinates of a tile
    def get_line_x_from_index(self, index):
        central_line_x = self.perspective_point_x
        spacing_x = self.V_LINES_SPACING * self.width

        # The -0.5 is there because our 0 in x will be the line to the left of the center.
        # So we shift by half a tile.
        offset = index - 0.5

        # We also need to add the global offset: self.current_offset_x
        line_x = central_line_x + offset*spacing_x + self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING * self.height
        # # We also need to add the global offset: self.current_offset_y
        line_y = spacing_y * index - self.current_offset_y
        return line_y

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y - self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def update_tiles(self):
        for i in range(0, self.NB_TILES):
            # We retrieve the tile and the tile_coordinates
            tile = self.tiles[i]
            tile_coordinates = self.tiles_coordinates[i]
            # xmin and ymin are the starting points of our tile. Adding 1 gives the maximum values.
            xmin, ymin = self.get_tile_coordinates(tile_coordinates[0], tile_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(tile_coordinates[0] + 1, tile_coordinates[1] + 1)

            # 2     3
            #
            # 1     4
            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)
            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_vertical_lines(self):
        start_index = -int(self.V_NB_LINES/2) + 1
        for i in range(start_index, start_index + self.V_NB_LINES):
            # Be careful, no floating-point numbers, and x1 and x2 have the same values because
            # the lines are vertical, so we created a variable line_x.
            line_x = self.get_line_x_from_index(i)
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.verticals_lines[i].points = [x1, y1, x2, y2]

    def init_horizontal_line(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):
        start_index = -int(self.V_NB_LINES / 2) + 1
        end_index = start_index + self.V_NB_LINES - 1
        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)
        for i in range(0, self.H_NB_LINES):
            # We start the horizontal lines at 0 (i = 0, so i * spacing_y = 0), and each new line
            # is spaced by spacing_y from the previous one.
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    # Writing the function for moving our game down
    def update(self, dt):
        # The delta time dt is a value returned by the update function,
        # we request a value of 1/60 = 0.01666, and the program tries to refresh at this rate, but
        # it is not precise, so we use this value to calculate a factor to add to our SPEED so that
        # in any case the speed is correct.
        time_factor = dt * 60
        # *60 because we are doing 1/60, so our value should be 1, and the difference creates the factor.
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()
        if not self.state_game_over and self.state_game_has_started:
            self.current_offset_y += self.speed * time_factor * self.height / 550
            # current_offset_y is subtracted in the update_horizontal_lines function within the for loop line_y
            spacing_y = self.H_LINES_SPACING * self.height
            # To always have lines to display, when a line passes y = 0, we modify
            # the coordinates so everything moves back. In other words, when the offset exceeds
            # the spacing, we subtract the spacing.
            # We replaced the next if statement with a while loop to avoid problems caused by very high speeds and
            # the first delta time, which would directly cause a game over.
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                # To have the tile move forward instead of looping back to the starting position,
                # we create a variable current_y_loop to count the number of loops and subtract it from the
                # tile's position at each loop in the get_tile_coordinates function.
                self.current_y_loop += 1
                self.score_txt = f'SCORE: {self.current_y_loop}'
                # We call generate_tiles_coordinates to create an infinite loop
                self.genegerate_tiles_coordinates()

            # Be careful to integrate current_offset_x into the calculation of xmax and xmin
            self.current_offset_x += self.current_speed_x * time_factor * self.width / 1200

        if not self.check_ship_collisions() and not self.state_game_over:
            self.state_game_over = True
            self.sound_music1.stop()
            self.sound_game_over_impact.play()
            Clock.schedule_once(self.play_voice_game_over, 2)
            self.menu_title = "G  A  M  E    O  V  E  R"
            self.difficulty_label = "RESTART"
            self.menu_widget.opacity = 1
            print("GAME OVER")

    # If we use Kivy's Clock in our function, we must add the dt parameter
    def play_voice_game_over(self, dt):
        if self.state_game_over:
            self.sound_game_over_voice.play()

    def on_menu_button_pressed(self, level):
        if self.state_game_over:
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        self.reset_game(level)
        self.state_game_has_started = True
        self.menu_widget.opacity = 0
        self.sound_music1.play()


class GalaxyApp(App):
    pass


GalaxyApp().run()
