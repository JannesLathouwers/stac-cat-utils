import os

import pystac
import datetime
import mimetypes
from rio_stac import create_stac_item

create_image_item = create_stac_item

media_types = {
    '.json': pystac.MediaType.JSON,
    '.txt': pystac.MediaType.TEXT,
    '.text': pystac.MediaType.TEXT,
    '.pdf': pystac.MediaType.PDF,
    '.xml': pystac.MediaType.XML,
    '.htm': pystac.MediaType.HTML,
    '.html': pystac.MediaType.HTML,
    '.yaml': 'text/yaml',
    '.yml': 'text/yaml',
    '.csv': 'text/csv',
}


def _get_file_creation_date(path):
    c_time = os.path.getctime(path)
    return datetime.datetime.fromtimestamp(c_time)


def create_file_item(href):
    _, extension = os.path.splitext(href)
    file_dt_creation = _get_file_creation_date(href)
    if extension.lower() in media_types:
        file_media_type = media_types[extension.lower()]
    else:
        file_media_type = mimetypes.guess_type(href)
    file_name = os.path.basename(href)
    file_asset = pystac.Asset(href=href, title=file_name,
                              media_type=file_media_type,
                              extra_fields={'Creation': file_dt_creation.strftime('%Y-%m-%d %H:%M')},
                              roles=['data'])
    return file_asset
