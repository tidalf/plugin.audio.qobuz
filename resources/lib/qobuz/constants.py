'''
    qobuz.constants
    ~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2018 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''

__debugging__ = 0


class ModeEnum(object):
    VIEW = 0x1
    PLAY = 0x2
    SCAN = 0x3
    VIEW_BIG_DIR = 0x4

    @classmethod
    def to_s(cls, mode):
        return cls._code_to_human[mode]


ModeEnum._code_to_human = {
    ModeEnum.VIEW: 'view',
    ModeEnum.PLAY: 'play',
    ModeEnum.SCAN: 'scan',
    ModeEnum.VIEW_BIG_DIR: 'view_big_dir'
}

Mode = ModeEnum

TEXT_IMAGE_TO_SIZE = {
    'xlarge': (1200, 1200),  # @todo remove, not in api
    'large': (800, 800),
    'small': (600, 600),
    'thumbnail':  (100, 100)
}
