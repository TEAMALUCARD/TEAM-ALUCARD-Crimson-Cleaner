"""Independent, read-only cleaning scan modules."""
from .browser_cache import BrowserCacheCleaner
from .prefetch import PrefetchCleaner
from .recycle_bin import RecycleBinCleaner
from .temp_files import TempFilesCleaner
from .windows_update import WindowsUpdateCleaner

__all__ = [
    "BrowserCacheCleaner",
    "PrefetchCleaner",
    "RecycleBinCleaner",
    "TempFilesCleaner",
    "WindowsUpdateCleaner",
]
