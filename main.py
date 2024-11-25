# pour modifier la taille de la fenetre lorsque l'on apuit sur run
# (cette config doit étre avant tout les import)
from kivy.config import Config
from kivy.core.audio import SoundLoader

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


Builder.load_file('menu.kv')

class MainWidget(RelativeLayout):
    # on import les fonctions contenu dans les fichier python exterieur au main
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

    SPEED = 3
    current_offset_y = 0
    current_y_loop = 0

    SPEED_X = 20
    current_offset_x = 0
    curent_speed_x = 0

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
    menu_button_title = StringProperty("START")

    score_txt = StringProperty('')

    sound_begin = None
    sound_galaxy = None
    sound_gameover_impact = None
    sound_gameover_voice = None
    sound_music1 = None
    sound_restart = None

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_audio()
        self.sound_galaxy.play()
        self.init_vertical_line()
        self.init_horizontal_line()
        self.init_tile()
        # important d'apellé le init_ship apres le init_tile pour que le vaisseau soit afficher au dessus
        # du parcours
        self.init_ship()
        self.reset_game()
        # on configure le clavier que lorque l'on est sur ordinateur car sinon le clavier du smartphone
        # va être afficher a l'ecran
        if self.is_desktop():

            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)
        # pour faire avancé le jeu, on utilise la fonction Clock avec notre update
        Clock.schedule_interval(self.update, 1.0 / 60)

    def init_audio(self):
        self.sound_begin = SoundLoader.load('audio/begin.wav')
        self.sound_galaxy = SoundLoader.load('audio/galaxy.wav')
        self.sound_gameover_impact = SoundLoader.load('audio/gameover_impact.wav')
        self.sound_gameover_voice = SoundLoader.load('audio/gameover_voice.wav')
        self.sound_music1 = SoundLoader.load('audio/music1.wav')
        self.sound_restart = SoundLoader.load('audio/restart.wav')

        self.sound_music1.volume = 1
        self.sound_begin.volume = .25
        self.sound_galaxy.volume = .25
        self.sound_gameover_voice.volume = .25
        self.sound_restart.volume = .25
        self.sound_gameover_impact.volume = .6

        self.sound_music1.loop = True

    def reset_game(self):
        self.current_offset_y = 0
        self.current_y_loop = 0
        self.score_txt = f'SCORE: {self.current_y_loop}'
        self.current_offset_x = 0
        self.curent_speed_x = 0
        self.tiles_coordinates = []

        self.pre_fill_tiles_coordinates()
        self.genegerate_tiles_coordinates()
        self.state_game_over = False

    # on a besoin de verifer si on est sur ordinateur ou sur smartphone
    def is_desktop(self):
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
        # on recupere les coordonné du vaisseau avant transformation pour pouvoir checké la colision
        self.ship_coordinates[0] = (center_x - half_width, base_y)
        self.ship_coordinates[1] = (center_x, base_y + height)
        self.ship_coordinates[2] = (center_x + half_width, base_y)
        # le * ici nous permet de lire les valeur contenu
        # dans le tuple et non le tuple lui meme
        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])
        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def check_ship_collisions(self):
        for i in range (0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            # condition de sortie de la boucle pour ne pas bouclé sur tout les valeur de ti_y car la collision
            # ne peut avoir lieux que avec la premier ou la deuxieme tile. donc si le ti_y et plus grand strictement
            # que la coordoné du deuxieme tile, on return False pour arrété de bouclé
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    def check_ship_collision_with_tile(self, ti_x, ti_y):
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x+1, ti_y+1)
        for i in range (0, len(self.ship_coordinates)):
            px, py = self.ship_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                # le point du vaiseau et a l'interieur du tile
                return True
        return False



    def init_tile(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range (0, self.NB_TILES):
                self.tiles.append(Quad())

    def pre_fill_tiles_coordinates(self):
        for i in range(0, 10):
            self.tiles_coordinates.append((0, i))

    def genegerate_tiles_coordinates(self):
        last_y = 0
        last_x = 0
        start_index = -int(self.V_NB_LINES / 2) + 1
        end_index = start_index + self.V_NB_LINES - 1

        # suprimer les coordonnées sorties de l'écran
        # ti_y < self.current_y_loop
        # on commence par la fin de tiles_coordinates vers le debut pour ne pas avoir de probleme avec les index
        # le 2eme -1 et car on souhaite regardé la valeur dans l'index 0
        # le 3eme pour parcourir a l'envers
        for i in range(len(self.tiles_coordinates) - 1, -1, -1):
            # on regarde si un tile a sa coordonné y (index [1]) qui est inférieur au nombre de boucle que
            # l'on a fait
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        # on doit se rapellé de la dérniere coordoné pour pouvoir modifier la valeur du last_y
        if len(self.tiles_coordinates) > 0:
            last_coordinate = self.tiles_coordinates[-1]
            last_x = last_coordinate[0]
            last_y = last_coordinate[1] + 1

        # la boucle for part de la taille de tiles_coordinates, ainsi lors de
        # l'init on créé NB_TILES tiles et
        # ensuite il faut dabort que la tile qui sort de lécran soit suprimé pour pouvoir recréé un tile
        for i in range(len(self.tiles_coordinates), self.NB_TILES):
            # pour la génération aléatoire du terrain:
            r = random.randint(0, 2)
            start_index = -int(self.V_NB_LINES / 2) + 1
            end_index = start_index + self.V_NB_LINES - 1
            if last_x <= start_index:
                r = 1
            if last_x >= end_index - 1:
                r = 2
            # 0 -> en avant
            # 1 -> droite
            # 2 -> gauche
            self.tiles_coordinates.append((last_x, last_y))
            if r == 1:
                last_x += 1  # tile de droite
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1  # tile de devant apres le déplacement a droite
                self.tiles_coordinates.append((last_x, last_y))
            elif r == 2:
                last_x -= 1  # tile de gauche
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1  # tile de devant apres le déplacement a droite
                self.tiles_coordinates.append((last_x, last_y))
            # on incrémente le last_y pour la prochaine serie
            last_y += 1


    def init_vertical_line(self):
        with self.canvas:
            Color(1, 1, 1)
            # self.line = Line(points=[100, 0, 100, 100])   pour créé une seul ligne
            for i in range(0, self.V_NB_LINES):
                self.verticals_lines.append(Line())

    # les fonction get_line_x_from_index et get_line_y_from_index on été créé affin de recuperer plus facilement
    # les coordonné d'un tiles(case)
    def get_line_x_from_index(self, index):
        central_line_x = self.perspective_point_x
        spacing_x = self.V_LINES_SPACING * self.width
        # le -0.5 est la car notre 0 en x sera la ligne a la gauche du centre.
        # On décale donc de la moitier d'une case
        offset = index - 0.5
        # on doit aussi ajouté le décalage global : self.current_offset_x
        line_x = central_line_x + offset*spacing_x + self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING * self.height
        # on doit aussi ajouté le décalage global : self.current_offset_y
        line_y = spacing_y * index - self.current_offset_y
        return line_y

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y - self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def update_tiles(self):
        for i in range(0, self.NB_TILES):
            # on recupere le tile et le tile_coordinates
            tile = self.tiles[i]
            tile_coordinates = self.tiles_coordinates[i]
            # xmin et ymin sont les points de départ de notre tile. si on ajout 1 on obtient les max
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
        """        ON ENLEVE TOUS LE CODE SUIVANT CAR ON A FAIT LA FONCTION get_line_x_from_index POUR
        AVOIR LA NOUVEL COORDONE DE X
        # self.line.points = [self.perspective_point_x, 0 ,self.perspective_point_y, 0]
        central_line_x = self.width / 2
        spacing_x = self.V_LINES_SPACING * self.width
        # vu que l'on choisi d'avoir une ligne central et de dessiné nos autres ligne depuis cette ligne
        # centrale,on va avoir besoin de commancé notre boucle dans le négatif. On definie donc
        # un offset
        # dans la suite du projet, on a choisie de suprimé la ligne central, de passé le nombre de ligne
        # de impair a pair et donc on a décallé l'Offset de 0.5 pour ne pas avoir de ligne centrale mais une "case"
        offset = -int(self.V_NB_LINES/2) + 0.5
        # pour 7 lignes l'offset nous fera donbc commencé à -3"""
        start_index = -int(self.V_NB_LINES/2) + 1
        for i in range(start_index, start_index + self.V_NB_LINES):
            # attention pas de nombre à virgule et x1 et x2 on les meme valeur car
            # les ligne sont vertical, on a donc écrit une variable line_x
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
        """ ON REMPLACE CE CODE PAR CE QUI SUIT DU FAIT D'AVOIR LA FONCTION get_line_x_from_index

        # pour que nos ligne sarrette a la derniere ligne vertical on recupére les calcul
        # de la fonction d'update vertical
        central_line_x = (self.width / 2)
        spacing = self.V_LINES_SPACING * self.width
        offset = -int(self.V_NB_LINES / 2) + 0.5
        # on reprend le meme calcul que pour line_x pour avoir le xmin
        xmin = central_line_x + offset * spacing + self.current_offset_x
        # on soustrait au lieux d'additionner pour avoir le xmax
        # (le max est - lofset car loffset et negatif donc - + - = +)
        xmax = central_line_x - offset * spacing + self.current_offset_x"""
        start_index = -int(self.V_NB_LINES / 2) + 1
        end_index = start_index + self.V_NB_LINES - 1
        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)
        for i in range(0, self.H_NB_LINES):
            # on commence les ligne horizontal a 0 (i = 0 donc i*spacing_y = 0) et puis chaque nouvel ligne
            # est espacer de sapcing_x par rapport a celle davant
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]




    # écriture de la fonction pour le déplacement de notre jeu vers le bas
    def update(self, dt):
        # le delta time dt est un valeur qui et retourné par la fonction update,
        # on demande un valeur de 1/ 60 = 0.01666 et le programme essaye de rafréchir a cette vitesse mais
        # n'est pas précis alors on utilise cette valeur pour calcules un facteur a ajouté a notre SPEED pour que
        # dans n'importe quelle cas la vitesse soit correcte
        time_factor = dt * 60
        # *60 car on fait 1/60 donc notre valeur devrait étre 1 et la difference créé alors le facteur
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()
        if not self.state_game_over and self.state_game_has_started:
            self.current_offset_y += self.SPEED * time_factor * self.height / 550
            # current_offset_y est soustrai dans la fonction update_horizontal_lines dans la boucle for line_y
            spacing_y = self.H_LINES_SPACING * self.height
            # pour avoir toujours des ligne a affiché, losque un ligne pass le y = 0, on remodifie
            # les coordonné pour que tout revienne en arriere. Autrement dit quand le décalage et superieur
            # a lespacement, on soustraie l'espacement
            # on a remplacer le prochain if par un while pour evité le probleme du au vitesse tres elevé et
            # au premier delta time qui va faire que l'on passe direct en game over
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                # pour avoir le tile qui avance au lieux de rebouclé et revenir a la position de départ,
                # on créé une variable current_y_loop pour compté le nombre de boucle et le soustraire de la
                # position du tile a chaque boucle dans le get_tile_coordinates
                self.current_y_loop += 1
                self.score_txt = f'SCORE: {self.current_y_loop}'
                # on rapelle generate_tiles_coordonates pour créé un boucle infinie
                self.genegerate_tiles_coordinates()

            # attention a integré le current_offset_x dans le calcul du xmax et xmin
            self.current_offset_x += self.curent_speed_x * time_factor * self.width / 1200

        if not self.check_ship_collisions() and not self.state_game_over:
            self.state_game_over = True
            self.sound_music1.stop()
            self.sound_gameover_impact.play()
            Clock.schedule_once(self.play_voice_game_over, 2)
            self.menu_title = "G  A  M  E    O  V  E  R"
            self.menu_button_title = "RESTART"
            self.menu_widget.opacity = 1
            print("GAME OVER")

    # si on utilise le Clock de kivy dans notre fonction, on doit ajouté le paramétre dt
    def play_voice_game_over(self, dt):
        if self.state_game_over:
            self.sound_gameover_voice.play()


    def on_menu_button_pressed(self):
        if self.state_game_over:
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        self.reset_game()
        self.state_game_has_started = True
        self.menu_widget.opacity = 0
        self.sound_music1.play()



    """ CODE QUI NE SERT PAS DANS LE JEU, JE LE GARDE POUR ME SOUVENIR DES FONCTIONS
    def on_parent(self, widget, parent):
        pass

    def on_size(self, *args):
        # a chaque fois que la fenetre est retailler, la fonction on_size est appelé
        # et donc on met a jour les lines vertical
        # self.update_vertical_lines()
        # self.update_horizontal_lines()
        # on a plus besoin de cette fonction car la fonction update rafraichi 60 fois par sec l'écran
        pass

    def on_perspective_point_x(self, widget, value):
        pass

    def on_perspective_point_y(self, widget, value):
        pass"""

class GalaxyApp(App):
    pass

GalaxyApp().run()