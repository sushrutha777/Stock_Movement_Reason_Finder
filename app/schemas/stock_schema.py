"""
Pydantic response models for the Stock Movement Reason Finder API.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class Headline(BaseModel):
    """A single news headline with its source link."""

    title: str = Field(..., description="Headline text")
    link: str = Field(..., description="URL to the full article")


class ReasonResponse(BaseModel):
    """Response for the /reason/{stock} endpoint."""

    stock: str = Field(..., description="Stock ticker symbol")
    change_percent: Optional[float] = Field(
        None, description="Percentage change over the analysis period"
    )
    reason: str = Field(..., description="AI-generated reasoning for price movement")
    headlines: List[Headline] = Field(
        default_factory=list, description="Recent news headlines used for reasoning"
    )


class SpikeResponse(BaseModel):
    """Response for the /spike/{stock} endpoint."""

    stock: str = Field(..., description="Stock ticker symbol")
    is_spike: bool = Field(..., description="Whether a spike was detected")
    change_percent: Optional[float] = Field(
        None, description="Latest percentage change"
    )
    threshold: float = Field(..., description="Spike detection threshold used")


class StockMover(BaseModel):
    """A single stock with its percentage change."""

    ticker: str = Field(..., description="Stock ticker symbol")
    change_percent: float = Field(..., description="Percentage change over the period")


class TopMoversResponse(BaseModel):
    """Response for the /top-movers endpoint."""

    period_days: int = Field(..., description="Number of days analyzed")
    top_gainers: List[StockMover] = Field(
        default_factory=list, description="Top gaining stocks"
    )
    top_losers: List[StockMover] = Field(
        default_factory=list, description="Top losing stocks"
    )
