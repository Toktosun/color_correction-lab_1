import cv2

from color_transfer import image_stats, _scale_array


class ColorCorrectionTransfer:
    preserve_paper = True
    clip = True

    def __init__(self, source, target):
        self.source = cv2.cvtColor(source, cv2.COLOR_BGR2LAB).astype("float32")
        self.target = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype("float32")

    @classmethod
    def image_stats(cls, image):
        l, a, b = cv2.split(image)
        (lMean, lStd) = (l.mean(), l.std())
        (aMean, aStd) = (a.mean(), a.std())
        (bMean, bStd) = (b.mean(), b.std())

        # return the color statistics
        return lMean, lStd, aMean, aStd, bMean, bStd

    def __subtract_by_target_image(self):
        l, a, b = cv2.split(self.target)
        (lMeanSrc, lStdSrc, aMeanSrc,
         aStdSrc, bMeanSrc, bStdSrc) = self.image_stats(self.source)
        (lMeanTar, lStdTar, aMeanTar,
         aStdTar, bMeanTar, bStdTar) = self.image_stats(self.target)

        l -= lMeanTar
        a -= aMeanTar
        b -= bMeanTar

        if self.preserve_paper:
            l = (lStdTar / lStdSrc) * l
            a = (aStdTar / aStdSrc) * a
            b = (bStdTar / bStdSrc) * b
        else:
            l = (lStdSrc / lStdTar) * l
            a = (aStdSrc / aStdTar) * a
            b = (bStdSrc / bStdTar) * b

        # add in the source mean
        l += lMeanSrc
        a += aMeanSrc
        b += bMeanSrc

        l = _scale_array(l, clip=self.clip)
        a = _scale_array(a, clip=self.clip)
        b = _scale_array(b, clip=self.clip)
        return l, a, b

    def get_converted_to_rgb(self):
        l, a, b = self.__subtract_by_target_image()
        transfer = cv2.merge([l, a, b])
        transfer = cv2.cvtColor(transfer.astype("uint8"), cv2.COLOR_LAB2BGR)
        return transfer
