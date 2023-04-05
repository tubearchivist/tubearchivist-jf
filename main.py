"""application entry point"""

from src.connect import Jellyfin, TubeArchivist, folder_check
from src.series import Library

folder_check()
Jellyfin().ping()
TubeArchivist().ping()


def main():
    """main thread"""
    library = Library()
    library.validate_series()


if __name__ == "__main__":
    main()
