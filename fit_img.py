from PIL import Image


class FitImg:
    def fit(self, img: Image, w: int, h: int):
        imw, imh = img.size
        side = min(w, h)

        if imw > imh:
            delta = side/imw
            neww, newh = side, int(imh*delta)
        else:
            delta = side/imh
            neww, newh = int(imw*delta), side

        return img.resize((neww, newh))