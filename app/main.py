"""application entry point"""

from src.connect import Jellyfin, TubeArchivist, env_check
from src.series import Library


def main():
    """main thread"""
    env_check()
    Jellyfin().ping()
    TubeArchivist().ping()

    library = Library()
    library.validate_series()


if __name__ == "__main__":
    main()
