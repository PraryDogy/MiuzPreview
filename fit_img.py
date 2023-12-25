from PIL import Image


class FitImg:
    def fit(self, img: Image, w: int, h: int):
        imw, imh = img.size

        if -3 < imw - imh < 3:
            imw, imh = imw, imw

        if w > h:

            print("horizontal window")

            if imw > imh:
                print("horizontal img")
                delta = imw/imh
                neww, newh = w, int(w/delta)
            else: # img h > img w
                print("vertical img")
                delta = imh/imw
                neww, newh = int(h/delta), h
        
        else:

            print("vertical window")

            if imw > imh:
                print("horizontal img")
                delta = imw/imh
                neww, newh = w, int(w/delta)
            else: # h > w and h > w
                print("vertival img")
                delta = imh/imw
                neww, newh = int(h/delta), h

        print("img", neww, newh)
        print("widget", w, h)

        return img.resize((neww, newh))