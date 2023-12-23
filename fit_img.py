from PIL import Image


class FitImg:
    def fit(self, img: Image, w: int, h: int):
        imw, imh = img.size

        if imw > imh:
            delta = w/imw
            neww, newh = w, int(imh*delta)
        else:
            delta = h/imh
            neww, newh = int(imw*delta), h

        return img.resize(size=(neww, newh))
    