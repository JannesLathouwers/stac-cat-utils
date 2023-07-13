from datetime import datetime
from typing import Any, Dict

import pystac
from pystac import Extent, ProviderRole, SpatialExtent, TemporalExtent
from pystac.extensions import sar, sat
from pystac.extensions.eo import Band
from pystac.extensions.item_assets import AssetDefinition
from pystac.link import Link
from pystac.utils import str_to_datetime

INSPIRE_METADATA_ASSET_KEY = "inspire-metadata"
SAFE_MANIFEST_ASSET_KEY = "safe-manifest"
PRODUCT_METADATA_ASSET_KEY = "product-metadata"

SENTINEL_LICENSE = Link(
    rel="license",
    target="https://sentinel.esa.int/documents/"
    + "247904/690755/Sentinel_Data_Legal_Notice",
)

SENTINEL_PLATFORMS = ["sentinel-1a", "sentinel-1b"]

SENTINEL_SLC_DESCRIPTION = (
    "Level-1 Single Look Complex (SLC) products are images in the slant range by azimuth imaging plane, in the image plane of satellite data acquisition. Each image pixel is represented by a complex (I and Q) magnitude value and therefore contains both amplitude and phase information. "  # noqa: E501
    "Each I and Q value is 16 bits per pixel. The processing for all SLC products results in a single look in each dimension using the full available signal bandwidth. The imagery is geo-referenced using orbit and attitude data from the satellite. SLC images are produced in a zero Doppler geometry. "   # noqa: E501
    "This convention is common with the standard slant range products available from other SAR sensors. The SM SLC Products contain one image per polarisation channel (i.e. one or two images) and are sampled at the natural pixel spacing. This means, the pixel spacing is determined, "    # noqa: E501
    "in azimuth by the pulse repetition frequency (PRF), and in range by the radar range sampling frequency. The IW SLC product contains one image per sub-swath, per polarisation channel, for a total of three or six images. Each sub-swath image consists of a series of bursts, where "    # noqa: E501
    "each burst was processed as a separate SLC image. The individually focused complex burst images are included, in azimuth-time order, into a single sub-swath image, with black-fill demarcation in between. Due to the one natural azimuth look inherent in the data, the imaged ground "  # noqa: E501
    "area of adjacent bursts will only marginally overlap in azimuth - just enough to provide contiguous coverage of the ground. Unlike SM and WV SLC products, which are sampled at the natural pixel spacing, the images for all bursts in all sub-swaths of an IW SLC product are re-sampled "   # noqa: E501
    "to a common pixel spacing grid in range and azimuth. The resampling to a common grid eliminates the need of further interpolation in case, in later processing stages, the bursts are merged to create a contiguous ground range, detected image. The EW SLC products contain one image per "  # noqa: E501
    "sub-swath, per polarisation channel, for a total of five or ten images. Each TOPSAR EW burst in a sub-swath is processed as a separate SLC image, and included in a sub-swath image exactly as in the IW case. Like the IW mode, EW is a one natural azimuth look mode, and therefore the EW "  # noqa: E501
    "and IW images have similar properties. As for the IW SLC products, the images for all bursts in all sub-swaths of an EW SLC product are re-sampled to a common pixel spacing grid in range and azimuth."   # noqa: E501
)

SENTINEL_SLC_START: datetime = str_to_datetime("2016-04-25T00:00:00Z")
SENTINEL_SLC_EXTENT = Extent(
    SpatialExtent([-180.0, -90.0, 180.0, 90.0]),
    TemporalExtent([[SENTINEL_SLC_START, None]]),
)

ACQUISITION_MODES = [
    "Stripmap (SM)",
    "Interferometric Wide Swath (IW)",
    "Extra Wide Swath (EW)",
    "Wave (WV)",
]
SENTINEL_CONSTELLATION = "sentinel-1"

SENTINEL_PROVIDER = pystac.Provider(
    name="ESA",
    roles=[
        ProviderRole.PRODUCER,
        ProviderRole.PROCESSOR,
        ProviderRole.LICENSOR,
    ],
    url="https://earth.esa.int/eogateway",
)

SENTINEL_SLC_PROVIDER = pystac.Provider(
    name="Sinergise",
    roles=[
        ProviderRole.HOST,
        ProviderRole.PROCESSOR,
        ProviderRole.LICENSOR,
    ],
    url="https://registry.opendata.aws/sentinel-1/",
)

SENTINEL_SLC_TECHNICAL_GUIDE = Link(
    title="Sentinel-1 Single Look Complex (SLC) Technical Guide",
    rel="about",
    target="https://sentinels.copernicus.eu/web/sentinel/technical-guides/sentinel-1-sar/products-algorithms/level-1-algorithms/single-look-complex",  # noqa: E501
)

SENTINEL_SLC_LICENSE = Link(
    title="Sentinel License",
    rel="license",
    target="https://scihub.copernicus.eu/twiki/do/view/SciHubWebPortal/TermsConditions",
)

SENTINEL_SLC_KEYWORDS = ["Single", "Look", "v", "sentinel", "copernicus", "esa", "sar"]


SENTINEL_POLARIZATIONS = {
    "vh": Band.create(
        name="VH",
        description="VH band: vertical transmit and horizontal receive",
    ),
    "hh": Band.create(
        name="HH",
        description="HH band: horizontal transmit and horizontal receive",
    ),
    "hv": Band.create(
        name="HV",
        description="HV band: horizontal transmit and vertical receive",
    ),
    "vv": Band.create(
        name="VV",
        description="VV band: vertical transmit and vertical receive",
    ),
}

SENTINEL_SLC_SAT = {
    "orbit_state": [sat.OrbitState.ASCENDING, sat.OrbitState.DESCENDING]
}

SENTINEL_SLC_SAR: Dict[str, Any] = {
    "looks_range": [2, 3, 5, 6],
    "product_type": ["SLC"],
    "looks_azimuth": [1, 2, 6],
    "polarizations": [
        sar.Polarization.HH,
        sar.Polarization.VV,
        sar.Polarization.HV,
        sar.Polarization.VH,
        [
            sar.Polarization.HH,
            sar.Polarization.HV,
        ],
        [
            sar.Polarization.VV,
            sar.Polarization.VH,
        ],
    ],
    "frequency_band": [sar.FrequencyBand.C],
    "instrument_mode": ["IW", "EW", "SM"],
    "center_frequency": [5.405],
    "resolution_range": [9, 20, 23, 50, 93],
    "resolution_azimuth": [9, 22, 23, 50, 87],
    "pixel_spacing_range": [3.5, 10, 25, 40],
    "observation_direction": [sar.ObservationDirection.RIGHT],
    "pixel_spacing_azimuth": [3.5, 10, 25, 40],
    "looks_equivalent_number": [3.7, 29.7, 398.4, 4.4, 81.8, 2.8, 10.7, 123.7],
}

SENTINEL_SLC_ASSETS = {
    "vh": AssetDefinition(
        {
            "title": "VH Data",
            "type": pystac.MediaType.COG,
            "description": "VH polarization backscattering coefficient, 16-bit DN.",
            "roles": ["data"],
        }
    ),
    "hh": AssetDefinition(
        {
            "title": "HH Data",
            "type": pystac.MediaType.COG,
            "description": "HH polarization backscattering coefficient, 16-bit DN.",
            "roles": ["data"],
        }
    ),
    "hv": AssetDefinition(
        {
            "title": "HV Data",
            "type": pystac.MediaType.COG,
            "description": "HV polarization backscattering coefficient, 16-bit DN.",
            "roles": ["data"],
        }
    ),
    "vv": AssetDefinition(
        {
            "title": "VV Data",
            "type": pystac.MediaType.COG,
            "description": "VV polarization backscattering coefficient, 16-bit DN.",
            "roles": ["data"],
        }
    ),
    "schema-calibration-hh": AssetDefinition(
        {
            "title": "HH Calibration Schema",
            "type": pystac.MediaType.XML,
            "description": (
                "Calibration metadata including calibration information and the beta nought, "
                "sigma nought, gamma and digital number look-up tables that can be used for "
                "absolute product calibration."
            ),
            "roles": ["metadata"],
        }
    ),
    "schema-calibration-hv": AssetDefinition(
        {
            "title": "HV Calibration Schema",
            "type": pystac.MediaType.XML,
            "description": (
                "Calibration metadata including calibration information and the beta nought, "
                "sigma nought, gamma and digital number look-up tables that can be used for "
                "absolute product calibration."
            ),
            "roles": ["metadata"],
        }
    ),
    "schema-calibration-vh": AssetDefinition(
        {
            "title": "VH Calibration Schema",
            "type": pystac.MediaType.XML,
            "description": (
                "Calibration metadata including calibration information and the beta nought, "
                "sigma nought, gamma and digital number look-up tables that can be used for "
                "absolute product calibration."
            ),
            "roles": ["metadata"],
        }
    ),
    "schema-calibration-vv": AssetDefinition(
        {
            "title": "VV Calibration Schema",
            "type": pystac.MediaType.XML,
            "description": (
                "Calibration metadata including calibration information and the beta nought, "
                "sigma nought, gamma and digital number look-up tables that can be used for "
                "absolute product calibration."
            ),
            "roles": ["metadata"],
        }
    ),
    "schema-noise-hh": AssetDefinition(
        {
            "title": "HH Noise Schema",
            "type": pystac.MediaType.XML,
            "description": "Estimated thermal noise look-up tables",
            "roles": ["metadata"],
        }
    ),
    "schema-noise-hv": AssetDefinition(
        {
            "title": "HV Noise Schema",
            "type": pystac.MediaType.XML,
            "description": "Estimated thermal noise look-up tables",
            "roles": ["metadata"],
        }
    ),
    "schema-noise-vh": AssetDefinition(
        {
            "title": "VH Noise Schema",
            "type": pystac.MediaType.XML,
            "description": "Estimated thermal noise look-up tables",
            "roles": ["metadata"],
        }
    ),
    "schema-noise-vv": AssetDefinition(
        {
            "title": "VV Noise Schema",
            "type": pystac.MediaType.XML,
            "description": "Estimated thermal noise look-up tables",
            "roles": ["metadata"],
        }
    ),
    "schema-product-hh": AssetDefinition(
        {
            "title": "HH Product Schema",
            "type": pystac.MediaType.XML,
            "description": (
                "Describes the main characteristics corresponding to the band: state of the "
                "platform during acquisition, image properties, Doppler information, geographic "
                "location, etc."
            ),
            "roles": ["metadata"],
        }
    ),
    "schema-product-hv": AssetDefinition(
        {
            "title": "HV Product Schema",
            "type": pystac.MediaType.XML,
            "description": (
                "Describes the main characteristics corresponding to the band: state of the "
                "platform during acquisition, image properties, Doppler information, geographic "
                "location, etc."
            ),
            "roles": ["metadata"],
        }
    ),
    "schema-product-vh": AssetDefinition(
        {
            "title": "VH Product Schema",
            "type": pystac.MediaType.XML,
            "description": (
                "Describes the main characteristics corresponding to the band: state of the "
                "platform during acquisition, image properties, Doppler information, geographic "
                "location, etc."
            ),
            "roles": ["metadata"],
        }
    ),
    "schema-product-vv": AssetDefinition(
        {
            "title": "VV Product Schema",
            "type": pystac.MediaType.XML,
            "description": (
                "Describes the main characteristics corresponding to the band: state of the "
                "platform during acquisition, image properties, Doppler information, geographic "
                "location, etc."
            ),
            "roles": ["metadata"],
        }
    ),
    "safe-manifest": AssetDefinition(
        {
            "title": "Manifest File",
            "type": pystac.MediaType.XML,
            "description": (
                "General product metadata in XML format. Contains a high-level textual "
                "description of the product and references to all of product's components, "
                "the product metadata, including the product identification and the resource "
                "references, and references to the physical location of each component file "
                "contained in the product."
            ),
            "roles": ["metadata"],
        }
    ),
    "thumbnail": AssetDefinition(
        {
            "title": "Preview Image",
            "type": pystac.MediaType.PNG,
            "description": (
                "An averaged, decimated preview image in PNG format. Single polarization "
                "products are represented with a grey scale image. Dual polarization products "
                "are represented by a single composite colour image in RGB with the red channel "
                "(R) representing the  co-polarization VV or HH), the green channel (G) "
                "represents the cross-polarization (VH or HV) and the blue channel (B) "
                "represents the ratio of the cross an co-polarizations."
            ),
            "roles": ["thumbnail"],
        }
    ),
}
