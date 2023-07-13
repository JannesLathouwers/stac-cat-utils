from typing import Dict, TypeVar

import pystac
from pystac.extensions.sar import (
    FrequencyBand,
    ObservationDirection,
    Polarization,
    SarExtension,
)
from pystac.extensions.sat import OrbitState, SatExtension
from stactools.core.io.xml import XmlElement

T = TypeVar("T", pystac.Item, pystac.Asset)


class ProductDataEntry:
    def __init__(
        self,
        resolution_rng: float,
        resolution_azi: float,
        pixel_spacing_rng: float,
        pixel_spacing_azi: float,
        no_looks_rng: int,
        no_looks_azi: int,
        enl: float,
    ):
        self.resolution_rng = resolution_rng
        self.resolution_azi = resolution_azi
        self.pixel_spacing_rng = pixel_spacing_rng
        self.pixel_spacing_azi = pixel_spacing_azi
        self.no_looks_rng = no_looks_rng
        self.no_looks_azi = no_looks_azi
        self.enl = enl


# Sourced from Sentinel-1 Product Definition: Table 5-1
#   https://sentinel.esa.int/web/sentinel/user-guides/sentinel-1-sar/document-library/-/asset_publisher/1dO7RF5fJMbd/content/sentinel-1-product-definition
#   https://sentinels.copernicus.eu/web/sentinel/technical-guides/sentinel-1-sar/products-algorithms/level-1-algorithms/single-look-complex
product_data_summary: Dict[str, ProductDataEntry] = {
    "SM": ProductDataEntry(1.7, 4.9, 1.5, 4.1, 1, 1, 1),
    "IW": ProductDataEntry(2.7, 22, 2.3, 14.1, 1, 1, 1),
    "EW": ProductDataEntry(7.9, 43, 5.9, 19.9, 1, 1, 1),
    "WV": ProductDataEntry(2.0, 4.8, 1.7, 4.1, 1, 1, 1),
}


def fill_sar_properties(
    sar_ext: SarExtension[T], manifest: XmlElement
) -> None:
    """Fills the properties for SAR.

    Based on the sar Extension.py

    Args:
        sar_ext (SarExtension): The extension to be populated.
        resolution (str): product resolution, needed to select metadata from
            static values in product_data_summary
        manifest (XmlElement): manifest.safe file parsed into an XmlElement
    """
    # Fixed properties
    sar_ext.frequency_band = FrequencyBand("C")
    sar_ext.center_frequency = 5.405
    sar_ext.observation_direction = ObservationDirection.RIGHT

    # Read properties
    instrument_mode = manifest.find_text(".//s1sarl1:mode")
    if instrument_mode:
        sar_ext.instrument_mode = instrument_mode
    sar_ext.polarizations = [
        Polarization(x.text)
        for x in manifest.findall(".//s1sarl1:transmitterReceiverPolarisation")
    ]
    product_type = manifest.find_text(".//s1sarl1:productType")
    if product_type:
        sar_ext.product_type = product_type

    # Properties depending on mode
    # https://sentinels.copernicus.eu/web/sentinel/technical-guides/sentinel-1-sar/products-algorithms/level-1/single-look-complex/interferometric-wide-swath
    # https://sentinels.copernicus.eu/web/sentinel/technical-guides/sentinel-1-sar/products-algorithms/level-1/single-look-complex/stripmap
    product_data = product_data_summary[sar_ext.instrument_mode]

    sar_ext.resolution_range = product_data.resolution_rng
    sar_ext.resolution_azimuth = product_data.resolution_azi
    sar_ext.pixel_spacing_range = product_data.pixel_spacing_rng
    sar_ext.pixel_spacing_azimuth = product_data.pixel_spacing_azi
    sar_ext.looks_range = product_data.no_looks_rng
    sar_ext.looks_azimuth = product_data.no_looks_azi
    sar_ext.looks_equivalent_number = product_data.enl


def fill_sat_properties(sat_ext: SatExtension[T], manifest: XmlElement) -> None:
    """Fills the properties for SAT.

    Based on the sat Extension.py

    Args:
        sat_ext (SatExtension): The extension to be populated.
        manifest (XmlElement): manifest.safe file parsed into an XmlElement
    """

    sat_ext.platform_international_designator = manifest.find_text(
        ".//safe:nssdcIdentifier"
    )

    orbit_state = manifest.find_text(".//s1:pass")
    if orbit_state:
        sat_ext.orbit_state = OrbitState(orbit_state.lower())

    orbit_number = manifest.find_text(".//safe:orbitNumber")
    if orbit_number:
        sat_ext.absolute_orbit = int(orbit_number)

    relative_orbit = manifest.find_text(".//safe:relativeOrbitNumber")
    if relative_orbit:
        sat_ext.relative_orbit = int(relative_orbit)
