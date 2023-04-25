import logging
import os
from typing import Optional, Tuple

import pystac
from pystac.extensions.eo import EOExtension

from eoepca_stac.slc.constants import SENTINEL_POLARIZATIONS

logger = logging.getLogger(__name__)


def image_asset_from_href(
    asset_href: str,
    item: pystac.Item,
    # resolution_to_shape: Dict[int, Tuple[int, int]],
    # proj_bbox: List[float],
    media_type: Optional[str] = None,
) -> Tuple[str, pystac.Asset]:
    logger.debug(f"Creating asset for image {asset_href}")

    _, ext = os.path.splitext(asset_href)
    if media_type is not None:
        asset_media_type = media_type
    else:
        if ext.lower() in [".tiff", ".tif"]:
            asset_media_type = pystac.MediaType.GEOTIFF
        else:
            raise Exception(f"Must supply a media type for asset : {asset_href}")

    # Handle band image
    split_filename = os.path.basename(asset_href).split(".")[0].split("-")
    if len(split_filename) == 2:
        band_id = split_filename[-1]
    else:
        band_id = f'{split_filename[1]}-{split_filename[3]}'

    if band_id is not None:
        band = SENTINEL_POLARIZATIONS[band_id.split('-')[1]]

        # Create asset
        desc = "Actual SAR data that have been processed into an image"
        asset = pystac.Asset(
            href=asset_href,
            media_type=asset_media_type,
            title=f"{band_id.split('-')[0].upper()} {band.name} Data",
            roles=["data"],
            description=desc,
        )

        asset_eo = EOExtension.ext(asset)
        asset_eo.bands = [SENTINEL_POLARIZATIONS[band_id.split('-')[1]]]

        return (band_id, asset)

    else:

        raise ValueError(f"Unexpected asset: {asset_href}")
