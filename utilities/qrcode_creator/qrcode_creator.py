from typing import Dict

import qrcode
from qrcode.image.pil import PilImage

from interfaces.creator_interface import CreatorInterface
from utilities.decorators.singleton import singleton


@singleton
class QRCodeCreator(CreatorInterface):
    """
    A class to generate a QR Code image
    """
    def create(self, data: Dict[str, object], fill_color: str = "black", back_color: str = "white",
               save_to: str = None, version: int = 10) -> PilImage:
        """
        Creates a PilImage of a QR Code image

        :param version: version of the QR Code - determines size
        :param data: data to insert into the QR Code
        :param fill_color: color to fill
        :param back_color: background color
        :param save_to: path to save image to
        :return: return PilImage of the QR Code
        """
        qr = qrcode.QRCode(
            version=version,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        if "url" in data:
            qr.add_data(data["url"], optimize=True)
        else:
            qr.add_data(str(data), optimize=True)

        qr.make(fit=True)
        img = qr.make_image(fill_color=fill_color, back_color=back_color)

        if save_to:
            if not save_to.endswith(".png"):
                save_to = save_to + ".png"
            with open(save_to, "wb") as img_file:
                img.save(img_file)

        return img
