"""Sector and asset-class presets for quick analysis."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SectorPreset:
    name: str
    description: str
    primary: str
    portfolio: tuple[str, ...]


SECTOR_PRESETS: dict[str, SectorPreset] = {
    "broad_market": SectorPreset(
        name="Broad Market",
        description="S&P 500 with bonds and gold as diversifiers.",
        primary="SPY",
        portfolio=("SPY", "TLT", "GLD"),
    ),
    "technology": SectorPreset(
        name="Technology",
        description="Tech sector ETF with Nasdaq and bonds.",
        primary="XLK",
        portfolio=("XLK", "QQQ", "TLT"),
    ),
    "financials": SectorPreset(
        name="Financials",
        description="Banks and regional financials with bond hedge.",
        primary="XLF",
        portfolio=("XLF", "KRE", "TLT"),
    ),
    "healthcare": SectorPreset(
        name="Healthcare",
        description="Healthcare sector with broad market and bonds.",
        primary="XLV",
        portfolio=("XLV", "SPY", "TLT"),
    ),
    "energy": SectorPreset(
        name="Energy",
        description="Energy sector with oil proxy and bonds.",
        primary="XLE",
        portfolio=("XLE", "USO", "TLT"),
    ),
    "international": SectorPreset(
        name="International",
        description="Developed and emerging markets ex-US.",
        primary="EFA",
        portfolio=("EFA", "EEM", "TLT"),
    ),
    "growth_value": SectorPreset(
        name="Growth vs Value",
        description="Compare growth and value factor ETFs.",
        primary="SPY",
        portfolio=("SPY", "IVW", "IVE"),
    ),
    "crypto_adjacent": SectorPreset(
        name="Crypto-Adjacent",
        description="Bitcoin ETF with tech and bonds (high risk).",
        primary="SPY",
        portfolio=("SPY", "IBIT", "TLT"),
    ),
}


def list_presets() -> list[SectorPreset]:
    return list(SECTOR_PRESETS.values())


def get_preset(key: str) -> SectorPreset:
    if key not in SECTOR_PRESETS:
        keys = ", ".join(SECTOR_PRESETS.keys())
        raise KeyError(f"Unknown preset '{key}'. Choose from: {keys}")
    return SECTOR_PRESETS[key]
