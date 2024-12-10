from kivy.uix.relativelayout import RelativeLayout


# We use a RelativeLayout so that it automatically takes the size of the parent instead of the widget,
# which initially takes a size of 100/100 px. To work, the parent must also be a RelativeLayout.
class MenuWidget(RelativeLayout):
    def on_touch_down(self, touch):
        # We disable the button if the menu is hidden.
        if self.opacity == 0:

            return False
        return super(RelativeLayout, self).on_touch_down(touch)
