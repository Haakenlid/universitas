from sorl.thumbnail.engines.wand_engine import Engine as WandEngine
from .boundingbox import Box, CropBox

import logging
logger = logging.getLogger(__name__)


def close_crop(x, y, left, right, top, bottom, aspect_ratio):
    l, r, t, b, A = left, right, top, bottom, aspect_ratio
    w, h = r - l, b - t
    a = w / h
    W = 0.5 * min(A, 1, w if a > A else h * A)
    H = W / A
    X, Y = [sorted(c)[1] for c in (
        ((W, (l + r) / 2, 1 - W), (l + W, x, r - W))[W * 2 < w],
        ((H, (t + b) / 2, 1 - H), (t + H, y, b - H))[H * 2 < h]
    )]
    return Box(X - W, Y - H, X + W, Y + H)


def calculate_crop(width, height, crop_width, crop_height, crop_box, exp):
    aspect_ratio = (crop_width * height) / (crop_height * width)

    # modify size of the crop box
    if exp < 0:  # shrink
        resize = exp, exp  # both axis
    elif aspect_ratio < 1:  # portrait
        resize = 0, exp  # grow height
    else:  # landscape
        resize = exp, 0  # grow width

    expanded_box = CropBox(**crop_box).expand(*resize).serialize()
    crop_to = close_crop(aspect_ratio=aspect_ratio, **expanded_box)

    return Box(
        int(crop_to.left * width),
        int(crop_to.top * height),
        int(crop_to.right * width),
        int(crop_to.bottom * height),
    )


class CloseCropEngine(WandEngine):

    def create(self, image, geometry, options):
        cropbox = options.pop('crop_box', None)
        expand = options.pop('expand', 0)
        if cropbox:
            new_geometry = calculate_crop(
                image.width, image.height,
                geometry[0], geometry[1],
                cropbox, expand,
            )
            image.crop(*new_geometry)

        return super().create(image, geometry, options)