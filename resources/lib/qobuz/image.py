import functools
import os
import requests

from qobuz import config
from qobuz.debug import getLogger
from qobuz.util.common import get_default_image_size
from qobuz.util.file import unlink
from qobuz.util.hash import hashit
from qobuz.util.random import randrange

COMBINED_COVER_FMT = 'cover-{nid}-{size_w}-{size_h}-{count}-combine.jpg'
TMPIMG_FMT = 'tmp-img.jpg'
HASHED_ALBUM_COVER_FMT = 'cache-album-cover-{}.jpg'

logger = getLogger(__name__)
PIL_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError as e:
    logger.error('Cannot import PIL library')


def _mywalk(path):
    for dirpath, _dirnames, filenames in os.walk(path):
        for name in filenames:
            yield name, os.path.join(dirpath, name)


def _find_all_combined_images(covers_path):
    for name, full_path in _mywalk(covers_path):
        if not name.endswith('.jpg'):
            continue
        yield full_path


def cleanfs_combined_covers():
    ''' Clean all images under __covers_path__
    '''
    covers_path = config.path.combined_covers
    for filename in _find_all_combined_images(covers_path):
        unlink(filename)


def next_image_generator_factory(images):
    ''' Yield image path from images array indefinitly (reset to 0)
    '''
    index = 0
    size = len(images)
    while True:
        if index >= size:
            index = 0
        ret = images[index]
        yield ret
        index += 1


def get_remote_image(url):
    ''' get image from url and return path from local file'''
    covers_path = config.path.combined_covers
    hashed_filename = HASHED_ALBUM_COVER_FMT.format(
        hashit(url))
    new_path = os.path.join(covers_path, hashed_filename)

    if not os.path.exists(new_path):
        img_request = requests.get(url, stream=True)
        if img_request.status_code != 200:
            logger.warn('GetRemoteImageError %s', img_request.status_code)
            return None
        with open(new_path, 'wb') as write_handle:
            write_handle.writelines(img_request.iter_content(1024))
            write_handle.flush()
    return new_path


def _resize_image(img_path, thumb_size_w):
    try:
        part = Image.open(img_path)
        new_height = thumb_size_w * part.height / part.width
        return part.resize((thumb_size_w, new_height), Image.ANTIALIAS)
    except Exception as e:
        logger.error('ResizeImageError %s', e)
    return None


def _combine_factory_final_path(count, nid, img_size):
    size_w, size_h = img_size
    covers_path = config.path.combined_covers
    filename = COMBINED_COVER_FMT.format(
        count=count,
        nid=nid,
        size_h=size_h,
        size_w=size_w
    )
    return os.path.join(covers_path, filename)


def _combine_factory_build_one(thumb_size,
                               image_path_generator,
                               new_image,
                               rowcol):
    img_path = next(image_path_generator)
    if img_path.startswith('http'):
        img_path = get_remote_image(img_path)
    image = _resize_image(img_path, thumb_size[0])
    new_image.paste(image, (rowcol[0] * thumb_size[0],
                            rowcol[1] * thumb_size[1]))


def _combine_factory_build(final_path, img_size, count, image_path_generator):
    new_image = Image.new('RGB', img_size)
    demi_count = count / 2
    thumb_size = (
        int(img_size[0] / demi_count),
        int(img_size[1] / demi_count)
    )

    for i in range(0, demi_count):
        for j in range(0, demi_count):
            _combine_factory_build_one(thumb_size,
                                       image_path_generator,
                                       new_image,
                                       (i, j))

    new_image.save(final_path)
    return final_path


def _combine_nopil(_nid, images=None):
    if not images:
        return None
    return images[randrange(0, len(images) - 1)]


def _combine_pil(nid, images=None):
    ''' Combine the first 4 images of images array into single image '''
    count = 4
    img_size = get_default_image_size()
    image_path_generator = next_image_generator_factory(images)
    final_path = _combine_factory_final_path(count, nid, img_size)
    if os.path.exists(final_path):
        return final_path
    return _combine_factory_build(final_path,
                                  img_size,
                                  count,
                                  image_path_generator)


def combine_factory(pil_available, nid, images=None):
    if not config.app.registry.get('image_create_mosaic', to='bool'):
        pil_available = False
    if pil_available is True and len(images) > 1:
        return _combine_pil(nid, images=images)
    return _combine_nopil(nid, images=images)


combine = functools.partial(combine_factory, PIL_AVAILABLE)
