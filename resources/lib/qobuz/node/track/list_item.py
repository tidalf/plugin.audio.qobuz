from kodi_six import xbmcgui

from qobuz.constants import Mode
from qobuz.debug import getLogger
from qobuz.gui.contextmenu import contextMenu

logger = getLogger(__name__)

trackTemplate = u'''- HiRes: {hires}
- HiRes purchased: {hires_purchased}
- purchasable: {purchasable}
- purchased: {purchased}
- streamable: {streamable}
- previewable: {previewable}
- sampleable: {sampleable}
- downloadable: {downloadable}
{description}
- label: {label}
- duration: {duration} mn
- track number: {track_number}
- year: {year}
- composer: {composer}
- performer: {performer}
- copyright: {copyright}
- popularity: {popularity}
- maximum sampling rate: {maximum_sampling_rate}
- maximum_bit_depth: {maximum_bit_depth}
'''


def make_list_item(node, **ka):
    replace_items = ka['replaceItems'] if 'replaceItems' in ka else False
    isplayable = 'true'
    item = xbmcgui.ListItem(
        node.get_label(),
        node.get_label2())
    item.setPath(node.make_url(mode=Mode.PLAY))
    item.setArt({
        'thumb': node.get_image(),
        'icon': node.get_image(img_type='thumbnail')
    })
    comment = trackTemplate.format(
        popularity=node.get_property(
            'popularity', default='n/a'),
        duration=node.get_duration(),
        label=node.get_album_label(),
        year=node.get_property('album/year'),
        performers=node.get_property('performers'),
        track_number=node.get_property('track_number'),
        version=node.get_property('version'),
        performer=node.get_property('performer/name'),
        composer=node.get_property('composer/name'),
        copyright=node.get_property(
            'copyright', default='n/a'),
        maximum_sampling_rate=node.get_maximum_sampling_rate(),
        maximum_bit_depth=node.get_maximum_bit_depth(),
        description=node.get_description(default=node.get_label()),
        hires=node.get_hires(),
        sampleable=node.get_sampleable(),
        downloadable=node.get_downloadable(),
        purchasable=node.get_purchasable(),
        purchased=node.get_purchased(),
        previewable=node.get_previewable(),
        streamable=node.get_streamable(),
        hires_purchased=node.get_hires_purchased(),
        awards=','.join(node.get_awards()),
        articles=', '.join(node.get_articles()))

    item.setInfo(
        type='Music',
        infoLabels={
            'count': node.nid,
            'title': node.get_title(),
            'album': node.get_album(),
            'genre': node.get_genre(),
            'artist': node.get_album_artist(),
            'tracknumber': node.get_track_number(default=0),
            'duration': node.get_property('duration'),
            'year': node.get_year(),
            'rating': str(node.get_popularity()),
        })
    item.setProperty('album_artist', node.get_album_artist())
    item.setProperty('album_description', comment)
    item.setProperty('album_label', node.get_property('album/label/name'))
    item.setProperty('Role.Composer', node.get_property('composer/name'))
    item.setProperty('DiscNumber', str(node.get_media_number(default=1)))
    item.setProperty('IsPlayable', isplayable)
    item.setProperty('IsInternetStream', isplayable)
    item.setProperty('Music', isplayable)
    ctxMenu = contextMenu()
    node.attach_context_menu(item, ctxMenu)
    item.addContextMenuItems(ctxMenu.getTuples(), replace_items)
    return item
