"""Create exaspim UI"""

from os import environ, name as osname

environ['PYOPENCL_COMPILER_OUTPUT'] = '1'

import argparse
from .userinterface import UserInterface
from coloredlogs import ColoredFormatter
import traceback
import logging
import sys
import ctypes
from pathlib import Path
import napari



from spim_core.config_base import Config

INSTALL_CONFIG_PATH = Path(__file__).parent / "config"
USER_CONFIG_PATH = Path().home() / "Documents" / ".exaspim_config"
# if config file present, user config file has priority


class SpimLogFilter(logging.Filter):
    # Note: add additional modules that we want to catch here.
    VALID_LOGGER_BASES = {"spim_core", "exaspim", "camera", "tigerasi"}

    def filter(self, record):
        """Returns true for a record that matches a log we want to keep."""
        return record.name.split(".")[0].lower() in self.__class__.VALID_LOGGER_BASES


def find_config_file(config_folder=None, simulated=False, file_name="config"):
    logger = logging.getLogger()
    allowed_extensions = [".toml", ".yaml"]
    simulated = "simulated" if simulated else ""
    if config_folder is not None:
        choices = [Path(config_folder) / simulated]
    else:
        choices = [
            Path(USER_CONFIG_PATH) / simulated,
            Path(INSTALL_CONFIG_PATH) / simulated,
        ]

    tried = []
    for config_folder in choices:
        for extension in allowed_extensions:
            config_path = (config_folder / (file_name + extension)).absolute()
            if config_path.is_file():
                logger.info(f"Using the config file {config_path}")
                return str(config_path)
            tried.append(str(config_path))

    msg = f"No config file could be found at either of these locations : {tried}"
    logger.error(msg)
    raise IOError(msg)


class create_UI:

    def __init__(self, config_folder=None, simulated=False):

        log_level = "DEBUG" # ["INFO", "DEBUG"]
        color_console_output = True

        # Setup logging.
        # Create log handlers to dispatch:
        # - User-specified level and above to print to console if specified.
        logger = logging.getLogger()  # get the root logger.
        # Remove any handlers already attached to the root logger.
        logging.getLogger().handlers.clear()
        # logger level must be set to the lowest level of any handler.
        logger.setLevel(logging.DEBUG)
        fmt = "%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s"
        fmt = "[SIM] " + fmt if simulated else fmt
        datefmt = "%Y-%m-%d,%H:%M:%S"
        log_formatter = (
            ColoredFormatter(fmt=fmt, datefmt=datefmt)
            if color_console_output
            else logging.Formatter(fmt=fmt, datefmt=datefmt)
        )

        log_handler = logging.StreamHandler(sys.stdout)
        log_handler.addFilter(SpimLogFilter())
        log_handler.setLevel(log_level)
        log_handler.setFormatter(log_formatter)
        logger.addHandler(log_handler)

        config_filepath = find_config_file(
            config_folder=config_folder, simulated=simulated
        )

        # Windows-based console needs to accept colored logs if running with color.
        if osname == "nt" and color_console_output:
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

        self.UI = UserInterface(
            config_filepath=config_filepath,
            console_output_level=log_level,
            simulated=simulated,
        )

        log_level = self.UI.cfg.cfg["debug"]["loglevel"]
        log_handler.setLevel(log_level)


def run_ui():
    parser = argparse.ArgumentParser(
        prog="exaspi-ui", description="Runs the Exaspim control software UI"
    )
    parser.add_argument("-cp", "--config_folder", default=None)
    parser.add_argument("-s", "--simulated", action="store_true")
    args = parser.parse_args()

    run = create_UI(args.config_folder, simulated=args.simulated)
    try:
        napari.run()
    finally:
        run.UI.close_instrument()


if __name__ == "__main__":

    run = create_UI()
    try:
        napari.run()
    finally:
        run.UI.close_instrument()
