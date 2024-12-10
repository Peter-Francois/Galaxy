def transform(self, x, y):
    # We use the transform function to make it easier to debug later.
    # return self.transform_2D(x, y)
    return self.transform_3D(x, y)


def transform_2D(self, x, y):
    # Be careful to always return integer values to avoid display issues.
    return int(x), int(y)


def transform_3D(self, x, y):
    # Cross multiplication to define the transformed position of the y point.
    lin_y = y * self.perspective_point_y / self.height
    if lin_y > self.perspective_point_y:
        lin_y = self.perspective_point_y
    diff_x = x - self.perspective_point_x
    # For the diff_y, it is important to take the transformed value of y: tr_y.
    diff_y = self.perspective_point_y - lin_y
    factor_y = diff_y / self.perspective_point_y
    # To reduce the perspective effect where the bottom box appears smaller than the top box,
    # we multiply the factor_y by itself.
    factor_y = pow(factor_y, 4)
    tr_x = self.perspective_point_x + diff_x * factor_y
    tr_y = self.perspective_point_y - factor_y * self.perspective_point_y

    # Be careful to always return integer values to avoid display issues
    return int(tr_x), int(tr_y)
