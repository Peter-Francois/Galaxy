from kivy.uix.relativelayout import RelativeLayout


def keyboard_closed(self):
    self._keyboard.unbind(on_key_down=self.on_keyboard_down)
    self._keyboard.unbind(on_key_up=self.on_keyboard_up)
    self._keyboard = None


# Definition of functions for pressing on the screen on the right or left.
def on_touch_down(self, touch):
    if not self.state_game_over and self.state_game_has_started:
        if touch.x < self.width / 2:
            self.current_speed_x = self.SPEED_X
        else:
            self.current_speed_x = -self.SPEED_X
        # To be able to press the menu button to start the game:
        # This function overrides the normal behavior of pressing a button.
        # If we want to pass the different calls according to the class inheritance, we need to call the super.
        # We should call the super of MainWidget, but it would lead to a recursive import because user_actions
        # depends on Main. So, we can call the parent class of MainWidget, which is RelativeLayout.
    return super(RelativeLayout, self).on_touch_down(touch)



# For managing the offset caused by the keyboard touch.
def on_touch_up(self, touch):
    self.current_speed_x = 0


def on_keyboard_down(self, keyboard, keycode, text, modifiers):
    if keycode[1] == 'left':
        self.current_speed_x = self.speed_x
    elif keycode[1] == 'right':
        self.current_speed_x = -self.speed_x
    return True


def on_keyboard_up(self, keyboard, keycode):
    self.current_speed_x = 0