from kivy.uix.relativelayout import RelativeLayout


# on utilise un RelativeLayout pour qu'il prenne automatiquement la taille du parent au lieux du widget
# qui prend la taille de 100/ 100 px a l'init, pour fonctionné, le parent doit etre aussi un RelativeLayout
class MenuWidget(RelativeLayout):
    def on_touch_down(self, touch):
        # on desactive le bouton si le menu est caché
        if self.opacity == 0:

            return False
        return super(RelativeLayout, self).on_touch_down(touch)
