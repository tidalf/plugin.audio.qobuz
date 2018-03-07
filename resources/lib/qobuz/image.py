import functools
from os import urandom
import requests

from qobuz import config
from qobuz import data_path
from qobuz.debug import getLogger
from qobuz.util.random import randrange


logger = getLogger(__name__)
available = False

try:
    from PIL import Image

    available = True
except ImportError as e:
    logger.error('Cannot import PIL library')


def combineFactory(available, nid, images=None, count=4, prefix='cover'):
    images = [] if images is None else images
    if not config.app.registry.get('image_create_mosaic', to='bool'):
        available = False
    len_images = len(images)
    if len_images == 0:
        return None
    if len_images == 1:
        return images[0]
    if available is False:
        return images[randrange(0, len_images)]
    final_path = os.path.join(
        data_path, '{prefix}-{nid}-combine.jpg'.format(
            prefix=prefix, nid=nid))
    if os.path.exists(final_path):
        return final_path
    full_size = 600
    new = Image.new('RGB', (full_size, full_size))
    total = 0
    demi_count = int(len_images / 2)
    size = full_size / demi_count
    for i in range(0, full_size, size):
        for j in range(0, full_size, size):
            img_path = images[total]
            if img_path.startswith('http'):
                tmp = os.path.join(data_path, 'tmp-img.jpg')
                r = requests.get(img_path, stream=True)
                with open(tmp, 'wb') as wh:
                    wh.writelines(r.iter_content(1024))
                path = tmp
            # sometimes there's no image
            try:
                part = Image.open(path)
                part = part.resize((size, size), Image.ANTIALIAS)
                new.paste(part, (i, j))
                total += 1
            except Exception as error:
                logger.error(error)
    new.save(final_path)
    return final_path


combine = functools.partial(combineFactory, available)
