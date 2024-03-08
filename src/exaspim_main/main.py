"""Create exaspim UI"""

import argparse
import os
from .userinterface import UserInterface
from coloredlogs import ColoredFormatter
import traceback
import logging
import sys
import ctypes
from pathlib import Path
import napari


CONFIG_PATH = Path(__file__).parent / "config"


class SpimLogFilter(logging.Filter):
    # Note: add additional modules that we want to catch here.
    VALID_LOGGER_BASES = {"spim_core", "exaspim", "camera", "tigerasi"}

    def filter(self, record):
        """Returns true for a record that matches a log we want to keep."""
        return record.name.split(".")[0].lower() in self.__class__.VALID_LOGGER_BASES


class create_UI:

    def __init__(self, config_folder=None, simulated=False):
        
        log_level = "INFO"  # ["INFO", "DEBUG"]
        color_console_output = True

        if config_folder is None :
            config_folder = CONFIG_PATH

        if simulated:
            config_path = str(Path(config_folder) / "simulated" / "config.toml")
        else:
            config_path = str(Path(config_folder) / "config.toml")

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

        # Windows-based console needs to accept colored logs if running with color.
        if os.name == "nt" and color_console_output:
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

        self.UI = UserInterface(
            config_filepath=config_path,
            console_output_level=log_level,
            simulated=simulated,
        )


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