from kivy.uix.relativelayout import RelativeLayout


def keyboard_closed(self):
    self._keyboard.unbind(on_key_down=self.on_keyboard_down)
    self._keyboard.unbind(on_key_up=self.on_keyboard_up)
    self._keyboard = None


# definition des fonction d'appuie sur l'écran a droite ou a gauche
def on_touch_down(self, touch):
    if not self.state_game_over and self.state_game_has_started:
        if touch.x < self.width / 2:
            self.current_speed_x = self.SPEED_X
        else:
            self.current_speed_x = -self.SPEED_X
        # Pour pouvoir apuiez sur la touch du menu pour démarer le jeu:
        # cette fonction vien surchargé le comportement normal de lapuit sur une touch(override)
        # si on souhaite transmettre les different appel par rapport au heritage de class, il faut appelé le super
        # on devrait metre le super de MainWidget mais on aurrait une importation recursive car user_actions
        # dépand du main. On peut donc metre la class parent du MainWidget qui est RelativeLayout
    return super(RelativeLayout, self).on_touch_down(touch)



# pour la gestion du dacalage par le touch du clavier
def on_touch_up(self, touch):
    self.current_speed_x = 0


def on_keyboard_down(self, keyboard, keycode, text, modifiers):
    if keycode[1] == 'left':
        self.current_speed_x = self.SPEED_X
    elif keycode[1] == 'right':
        self.current_speed_x = -self.SPEED_X
    return True


def on_keyboard_up(self, keyboard, keycode):
    self.current_speed_x = 0