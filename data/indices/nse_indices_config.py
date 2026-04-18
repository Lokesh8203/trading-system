"""
NSE Sectoral and Custom Indices Configuration

Comprehensive index tracking for NSE sectors to identify
trading opportunities across different market segments.

Supports:
- Standard NSE indices (Nifty 50, Bank Nifty, etc.)
- Sectoral indices (Auto, Pharma, IT, etc.)
- Custom indices built from NSE 200/500 stocks
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class IndexConfig:
    """Configuration for an index"""
    name: str
    symbol: str  # Trading symbol or custom identifier
    constituents: List[str] = None  # List of stock symbols
    sector: str = None
    description: str = ""
    is_custom: bool = False
    yahoo_symbol: str = None  # For yfinance data fetching


# ============================================================================
# STANDARD NSE INDICES
# ============================================================================

STANDARD_INDICES = {
    'NIFTY50': IndexConfig(
        name='Nifty 50',
        symbol='NIFTY',
        yahoo_symbol='^NSEI',
        sector='Broad Market',
        description='Top 50 companies by market cap on NSE',
        is_custom=False
    ),
    'NIFTY_NEXT50': IndexConfig(
        name='Nifty Next 50',
        symbol='NIFTY_NEXT50',
        yahoo_symbol='^NSMIDCP',
        sector='Broad Market',
        description='Next 50 companies after Nifty 50',
        is_custom=False
    ),
    'NIFTY100': IndexConfig(
        name='Nifty 100',
        symbol='NIFTY100',
        sector='Broad Market',
        description='Nifty 50 + Nifty Next 50',
        is_custom=False
    ),
    'NIFTY200': IndexConfig(
        name='Nifty 200',
        symbol='NIFTY200',
        sector='Broad Market',
        description='Top 200 companies',
        is_custom=False
    ),
    'NIFTY500': IndexConfig(
        name='Nifty 500',
        symbol='NIFTY500',
        sector='Broad Market',
        description='Top 500 companies - broad market representation',
        is_custom=False
    ),
    'NIFTY_MIDCAP50': IndexConfig(
        name='Nifty Midcap 50',
        symbol='NIFTY_MIDCAP50',
        sector='Midcap',
        description='Top 50 midcap companies',
        is_custom=False
    ),
    'NIFTY_MIDCAP100': IndexConfig(
        name='Nifty Midcap 100',
        symbol='NIFTY_MIDCAP100',
        sector='Midcap',
        description='Top 100 midcap companies',
        is_custom=False
    ),
    'NIFTY_SMALLCAP100': IndexConfig(
        name='Nifty Smallcap 100',
        symbol='NIFTY_SMALLCAP100',
        sector='Smallcap',
        description='Top 100 smallcap companies',
        is_custom=False
    ),
    'BANKNIFTY': IndexConfig(
        name='Bank Nifty',
        symbol='BANKNIFTY',
        yahoo_symbol='^NSEBANK',
        sector='Banking',
        description='Banking sector index - top 12 banking stocks',
        is_custom=False
    ),
}


# ============================================================================
# SECTORAL INDICES (NSE Official)
# ============================================================================

SECTORAL_INDICES = {
    # Financial Services
    'NIFTY_FIN_SERVICE': IndexConfig(
        name='Nifty Financial Services',
        symbol='NIFTY_FIN_SERVICE',
        sector='Financial Services',
        description='Banks, NBFCs, Insurance, AMCs',
        is_custom=False
    ),

    # Auto
    'NIFTY_AUTO': IndexConfig(
        name='Nifty Auto',
        symbol='NIFTY_AUTO',
        sector='Automobile',
        description='Auto manufacturers and auto ancillaries',
        is_custom=False
    ),

    # Pharma
    'NIFTY_PHARMA': IndexConfig(
        name='Nifty Pharma',
        symbol='NIFTY_PHARMA',
        sector='Pharmaceuticals',
        description='Pharmaceutical and healthcare companies',
        is_custom=False
    ),

    # IT
    'NIFTY_IT': IndexConfig(
        name='Nifty IT',
        symbol='NIFTY_IT',
        sector='Information Technology',
        description='IT services and software companies',
        is_custom=False
    ),

    # FMCG
    'NIFTY_FMCG': IndexConfig(
        name='Nifty FMCG',
        symbol='NIFTY_FMCG',
        sector='FMCG',
        description='Fast Moving Consumer Goods',
        is_custom=False
    ),

    # Metal
    'NIFTY_METAL': IndexConfig(
        name='Nifty Metal',
        symbol='NIFTY_METAL',
        sector='Metals',
        description='Steel, Aluminum, Copper, Mining',
        is_custom=False
    ),

    # Realty
    'NIFTY_REALTY': IndexConfig(
        name='Nifty Realty',
        symbol='NIFTY_REALTY',
        sector='Real Estate',
        description='Real estate developers and infrastructure',
        is_custom=False
    ),

    # Energy
    'NIFTY_ENERGY': IndexConfig(
        name='Nifty Energy',
        symbol='NIFTY_ENERGY',
        sector='Energy',
        description='Oil & Gas, Power generation',
        is_custom=False
    ),

    # Media
    'NIFTY_MEDIA': IndexConfig(
        name='Nifty Media',
        symbol='NIFTY_MEDIA',
        sector='Media',
        description='Media, Entertainment, Broadcasting',
        is_custom=False
    ),

    # PSU Bank
    'NIFTY_PSU_BANK': IndexConfig(
        name='Nifty PSU Bank',
        symbol='NIFTY_PSU_BANK',
        sector='PSU Banking',
        description='Public Sector Banks',
        is_custom=False
    ),

    # Private Bank
    'NIFTY_PVT_BANK': IndexConfig(
        name='Nifty Private Bank',
        symbol='NIFTY_PVT_BANK',
        sector='Private Banking',
        description='Private Sector Banks',
        is_custom=False
    ),

    # Infrastructure
    'NIFTY_INFRA': IndexConfig(
        name='Nifty Infrastructure',
        symbol='NIFTY_INFRA',
        sector='Infrastructure',
        description='Infrastructure development companies',
        is_custom=False
    ),

    # Commodities
    'NIFTY_COMMODITIES': IndexConfig(
        name='Nifty Commodities',
        symbol='NIFTY_COMMODITIES',
        sector='Commodities',
        description='Companies in commodity business',
        is_custom=False
    ),

    # Consumption
    'NIFTY_CONSUMPTION': IndexConfig(
        name='Nifty India Consumption',
        symbol='NIFTY_CONSUMPTION',
        sector='Consumption',
        description='Consumer-facing businesses',
        is_custom=False
    ),

    # Oil & Gas
    'NIFTY_OIL_GAS': IndexConfig(
        name='Nifty Oil & Gas',
        symbol='NIFTY_OIL_GAS',
        sector='Oil & Gas',
        description='Upstream and downstream oil companies',
        is_custom=False
    ),

    # Healthcare
    'NIFTY_HEALTHCARE': IndexConfig(
        name='Nifty Healthcare',
        symbol='NIFTY_HEALTHCARE',
        sector='Healthcare',
        description='Healthcare services and pharmaceuticals',
        is_custom=False
    ),
}


# ============================================================================
# CUSTOM SECTORAL INDICES (Built from NSE200/500 stocks)
# ============================================================================

# Chemicals Sector (Custom)
CUSTOM_INDICES = {
    'NIFTY_CHEMICALS_CUSTOM': IndexConfig(
        name='Nifty Chemicals (Custom)',
        symbol='NIFTY_CHEMICALS_CUSTOM',
        sector='Chemicals',
        description='Custom chemical sector index',
        is_custom=True,
        constituents=[
            'PIDILITIND.NS',  # Pidilite Industries
            'AARTI.NS',       # Aarti Industries
            'DEEPAKNTR.NS',   # Deepak Nitrite
            'SRF.NS',         # SRF Ltd
            'TATACHEM.NS',    # Tata Chemicals
            'NAVINFLUOR.NS',  # Navin Fluorine
            'BALRAMCHIN.NS',  # Balrampur Chini (Chemical segment)
            'ALKYLAMINE.NS',  # Alkyl Amines
            'CLEAN.NS',       # Clean Science
            'FINEORG.NS',     # Fine Organics
        ]
    ),

    # Defense Sector (Custom)
    'NIFTY_DEFENSE_CUSTOM': IndexConfig(
        name='Nifty Defense (Custom)',
        symbol='NIFTY_DEFENSE_CUSTOM',
        sector='Defense',
        description='Custom defense and aerospace index',
        is_custom=True,
        constituents=[
            'HAL.NS',         # Hindustan Aeronautics
            'BDL.NS',         # Bharat Dynamics
            'BEL.NS',         # Bharat Electronics
            'GRSE.NS',        # GRSE (shipbuilding)
            'COCHINSHIP.NS',  # Cochin Shipyard
            'MAZAGON.NS',     # Mazagon Dock
            'SOLARA.NS',      # Solar Industries (explosives)
            'DATAMATICS.NS',  # Datamatics (defense IT)
        ]
    ),

    # Renewable Energy (Custom)
    'NIFTY_RENEWABLES_CUSTOM': IndexConfig(
        name='Nifty Renewables (Custom)',
        symbol='NIFTY_RENEWABLES_CUSTOM',
        sector='Renewable Energy',
        description='Custom renewable energy index',
        is_custom=True,
        constituents=[
            'ADANIGREEN.NS',  # Adani Green Energy
            'SUZLON.NS',      # Suzlon Energy
            'TATAPOWER.NS',   # Tata Power (renewable segment)
            'POWERGRID.NS',   # Power Grid
            'NTPC.NS',        # NTPC (green energy)
            'JINDALSAW.NS',   # Jindal Saw (solar)
            'WEBELSOLAR.NS',  # Websol Energy
            'VIKRAMCEMENTING.NS', # Vikramcementing (waste energy)
        ]
    ),

    # E-Commerce & Digital (Custom)
    'NIFTY_DIGITAL_CUSTOM': IndexConfig(
        name='Nifty Digital Economy (Custom)',
        symbol='NIFTY_DIGITAL_CUSTOM',
        sector='Digital Economy',
        description='E-commerce, fintech, digital services',
        is_custom=True,
        constituents=[
            'ZOMATO.NS',      # Zomato
            'PAYTM.NS',       # Paytm
            'NYKAA.NS',       # Nykaa
            'POLICYBZR.NS',   # Policybazaar
            'INDIAMART.NS',   # IndiaMART
            'JUSTDIAL.NS',    # Just Dial
            'INFO.NS',        # Info Edge (Naukri)
            'ROUTE.NS',       # Route Mobile
        ]
    ),

    # Logistics & Transportation (Custom)
    'NIFTY_LOGISTICS_CUSTOM': IndexConfig(
        name='Nifty Logistics (Custom)',
        symbol='NIFTY_LOGISTICS_CUSTOM',
        sector='Logistics',
        description='Transportation and logistics companies',
        is_custom=True,
        constituents=[
            'BLUEDART.NS',    # Blue Dart
            'TCI.NS',         # TCI (Transport Corp)
            'VRL.NS',         # VRL Logistics
            'MAHLOG.NS',      # Mahindra Logistics
            'GATI.NS',        # Gati Ltd
            'CONCOR.NS',      # Container Corporation
            'GATEWAY.NS',     # Gateway Distriparks
        ]
    ),

    # Textiles (Custom)
    'NIFTY_TEXTILES_CUSTOM': IndexConfig(
        name='Nifty Textiles (Custom)',
        symbol='NIFTY_TEXTILES_CUSTOM',
        sector='Textiles',
        description='Textile and apparel companies',
        is_custom=True,
        constituents=[
            'ARVIND.NS',      # Arvind Ltd
            'TRIDENT.NS',     # Trident Ltd
            'WELSPUN.NS',     # Welspun India
            'GRASIM.NS',      # Grasim (textile segment)
            'RAYMOND.NS',     # Raymond
            'SPTL.NS',        # Siyaram Silk
            'VARDHMAN.NS',    # Vardhman Textiles
            'NITIN.NS',       # Nitin Spinners
        ]
    ),

    # Specialty Retail (Custom)
    'NIFTY_RETAIL_CUSTOM': IndexConfig(
        name='Nifty Retail (Custom)',
        symbol='NIFTY_RETAIL_CUSTOM',
        sector='Retail',
        description='Organized retail chains',
        is_custom=True,
        constituents=[
            'DMART.NS',       # DMart
            'TRENT.NS',       # Trent (Westside, Zudi)
            'SHOPERSTOP.NS', # Shoppers Stop
            'TITAN.NS',       # Titan (jewelry retail)
            'RELAXO.NS',      # Relaxo Footwear
            'VMART.NS',       # V-Mart Retail
            'ADITYA.NS',      # Aditya Birla Fashion
        ]
    ),

    # Capital Goods (Custom)
    'NIFTY_CAPGOODS_CUSTOM': IndexConfig(
        name='Nifty Capital Goods (Custom)',
        symbol='NIFTY_CAPGOODS_CUSTOM',
        sector='Capital Goods',
        description='Engineering and capital goods',
        is_custom=True,
        constituents=[
            'LT.NS',          # L&T
            'SIEMENS.NS',     # Siemens
            'ABB.NS',         # ABB India
            'THERMAX.NS',     # Thermax
            'CUMMINS.NS',     # Cummins India
            'BHEL.NS',        # BHEL
            'KARAM.NS',       # KEI Industries
            'KALPATPOWR.NS',  # Kalpataru Power
        ]
    ),

    # PSU (Custom - excluding banks)
    'NIFTY_PSU_CUSTOM': IndexConfig(
        name='Nifty PSU (Custom)',
        symbol='NIFTY_PSU_CUSTOM',
        sector='PSU',
        description='Public Sector Undertakings (non-banking)',
        is_custom=True,
        constituents=[
            'NTPC.NS',        # NTPC
            'POWERGRID.NS',   # Power Grid
            'COAL.NS',        # Coal India
            'ONGC.NS',        # ONGC
            'GAIL.NS',        # GAIL
            'IOC.NS',         # Indian Oil
            'BPCL.NS',        # BPCL
            'SAIL.NS',        # SAIL
            'NMDC.NS',        # NMDC
            'HAL.NS',         # HAL
        ]
    ),

    # Hotels & Tourism (Custom)
    'NIFTY_TOURISM_CUSTOM': IndexConfig(
        name='Nifty Tourism (Custom)',
        symbol='NIFTY_TOURISM_CUSTOM',
        sector='Tourism',
        description='Hotels, travel, and tourism',
        is_custom=True,
        constituents=[
            'INDHOTEL.NS',    # Indian Hotels (Taj)
            'LEMONTREE.NS',   # Lemon Tree Hotels
            'CHALET.NS',      # Chalet Hotels
            'MAHLIFE.NS',     # Mahindra Holidays
            'TCS.NS',         # Thomas Cook (if listed)
            'EIHLTD.NS',      # EIH (Oberoi)
        ]
    ),
}


# ============================================================================
# THEMATIC INDICES (Momentum, Quality, Low Volatility, etc.)
# ============================================================================

THEMATIC_INDICES = {
    'NIFTY_ALPHA50': IndexConfig(
        name='Nifty Alpha 50',
        symbol='NIFTY_ALPHA50',
        sector='Thematic',
        description='High alpha stocks - risk-adjusted returns',
        is_custom=False
    ),
    'NIFTY_QUALITY30': IndexConfig(
        name='Nifty Quality 30',
        symbol='NIFTY_QUALITY30',
        sector='Thematic',
        description='High quality companies - ROE, debt, earnings',
        is_custom=False
    ),
    'NIFTY_LOW_VOL50': IndexConfig(
        name='Nifty Low Volatility 50',
        symbol='NIFTY_LOW_VOL50',
        sector='Thematic',
        description='Low volatility stocks for stable returns',
        is_custom=False
    ),
    'NIFTY_DIVIDEND': IndexConfig(
        name='Nifty Dividend Opportunities 50',
        symbol='NIFTY_DIVIDEND',
        sector='Thematic',
        description='High dividend yield stocks',
        is_custom=False
    ),
    'NIFTY_GROWTH_SECTORS': IndexConfig(
        name='Nifty Growth Sectors 15',
        symbol='NIFTY_GROWTH_SECTORS',
        sector='Thematic',
        description='High growth potential sectors',
        is_custom=False
    ),
}


# ============================================================================
# COMBINED INDEX DICTIONARY
# ============================================================================

ALL_INDICES = {
    **STANDARD_INDICES,
    **SECTORAL_INDICES,
    **CUSTOM_INDICES,
    **THEMATIC_INDICES
}


# ============================================================================
# INDEX GROUPS FOR ANALYSIS
# ============================================================================

INDEX_GROUPS = {
    'broad_market': [
        'NIFTY50', 'NIFTY100', 'NIFTY200', 'NIFTY500',
        'NIFTY_NEXT50', 'BANKNIFTY'
    ],

    'market_cap': [
        'NIFTY_MIDCAP50', 'NIFTY_MIDCAP100', 'NIFTY_SMALLCAP100'
    ],

    'core_sectors': [
        'NIFTY_IT', 'NIFTY_PHARMA', 'NIFTY_AUTO',
        'NIFTY_FMCG', 'NIFTY_METAL', 'NIFTY_ENERGY'
    ],

    'banking_financial': [
        'BANKNIFTY', 'NIFTY_FIN_SERVICE',
        'NIFTY_PSU_BANK', 'NIFTY_PVT_BANK'
    ],

    'emerging_sectors': [
        'NIFTY_CHEMICALS_CUSTOM', 'NIFTY_DEFENSE_CUSTOM',
        'NIFTY_RENEWABLES_CUSTOM', 'NIFTY_DIGITAL_CUSTOM'
    ],

    'cyclical': [
        'NIFTY_AUTO', 'NIFTY_REALTY', 'NIFTY_METAL',
        'NIFTY_INFRA', 'NIFTY_CAPGOODS_CUSTOM'
    ],

    'defensive': [
        'NIFTY_PHARMA', 'NIFTY_FMCG', 'NIFTY_HEALTHCARE'
    ],

    'custom_all': list(CUSTOM_INDICES.keys()),

    'thematic_all': list(THEMATIC_INDICES.keys()),
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_index_config(index_symbol: str) -> IndexConfig:
    """Get configuration for a specific index"""
    return ALL_INDICES.get(index_symbol)


def get_indices_by_sector(sector: str) -> List[IndexConfig]:
    """Get all indices for a specific sector"""
    return [
        config for config in ALL_INDICES.values()
        if config.sector.lower() == sector.lower()
    ]


def get_custom_indices() -> Dict[str, IndexConfig]:
    """Get all custom-built indices"""
    return CUSTOM_INDICES


def get_standard_indices() -> Dict[str, IndexConfig]:
    """Get all standard NSE indices"""
    return {**STANDARD_INDICES, **SECTORAL_INDICES}


def get_index_group(group_name: str) -> List[str]:
    """Get list of index symbols for a predefined group"""
    return INDEX_GROUPS.get(group_name, [])


def list_all_sectors() -> List[str]:
    """Get list of all unique sectors"""
    sectors = set()
    for config in ALL_INDICES.values():
        if config.sector:
            sectors.add(config.sector)
    return sorted(list(sectors))


# ============================================================================
# WATCHLIST PRESETS
# ============================================================================

WATCHLIST_PRESETS = {
    'primary': [
        'NIFTY50', 'BANKNIFTY', 'NIFTY_IT', 'NIFTY_AUTO',
        'NIFTY_PHARMA', 'NIFTY_METAL'
    ],

    'sectoral_rotation': [
        'NIFTY_AUTO', 'NIFTY_PHARMA', 'NIFTY_IT', 'NIFTY_METAL',
        'NIFTY_REALTY', 'NIFTY_FMCG', 'NIFTY_ENERGY', 'NIFTY_FIN_SERVICE'
    ],

    'emerging_themes': [
        'NIFTY_CHEMICALS_CUSTOM', 'NIFTY_DEFENSE_CUSTOM',
        'NIFTY_RENEWABLES_CUSTOM', 'NIFTY_DIGITAL_CUSTOM',
        'NIFTY_LOGISTICS_CUSTOM'
    ],

    'volatility_play': [
        'NIFTY50', 'NIFTY_MIDCAP100', 'NIFTY_SMALLCAP100',
        'NIFTY_LOW_VOL50'
    ],

    'quality_focus': [
        'NIFTY_QUALITY30', 'NIFTY_ALPHA50', 'NIFTY_DIVIDEND'
    ],

    'all_sectoral': list(SECTORAL_INDICES.keys()),

    'all_custom': list(CUSTOM_INDICES.keys()),
}


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    'IndexConfig',
    'ALL_INDICES',
    'STANDARD_INDICES',
    'SECTORAL_INDICES',
    'CUSTOM_INDICES',
    'THEMATIC_INDICES',
    'INDEX_GROUPS',
    'WATCHLIST_PRESETS',
    'get_index_config',
    'get_indices_by_sector',
    'get_custom_indices',
    'get_standard_indices',
    'get_index_group',
    'list_all_sectors',
]
