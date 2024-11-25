def transform(self, x, y):
    # On passe part la fonction transform pour pouvoir mieux débugé par la suite
    # return self.transform_2D(x, y)
    return self.transform_3D(x, y)


def transform_2D(self, x, y):
    # attention a toujours retourné des valeur entier pour evité les problème d'affichage
    return int(x), int(y)


def transform_3D(self, x, y):
    # produit en croix pour definir la position transformer du point y
    lin_y = y * self.perspective_point_y / self.height
    # Blinder le code, utile???
    if lin_y > self.perspective_point_y:
        lin_y = self.perspective_point_y
    diff_x = x - self.perspective_point_x
    # pour le diff_y il est importent de prendre la valeur transformée de y : tr_y
    diff_y = self.perspective_point_y - lin_y
    factor_y = diff_y / self.perspective_point_y
    # pour reduir l'effet en perspective que le case du bas paret plus petite que la case du heut,
    # on multiplie le facteur_y par lui meme
    factor_y = pow(factor_y, 4)
    tr_x = self.perspective_point_x + diff_x * factor_y
    tr_y = self.perspective_point_y - factor_y * self.perspective_point_y

    # attention a toujours retourné des valeur entier pour evité les problème d'affichage
    return int(tr_x), int(tr_y)
