"""Data collectors for AI News Reporter."""

from .base import BaseCollector
from .scraper import WebScraper
from .tavily_search import TavilyCollector

__all__ = ["BaseCollector", "TavilyCollector", "WebScraper"]
