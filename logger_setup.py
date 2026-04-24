import logging
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# All log output goes to workflow.log in the project root
LOG_PATH = os.path.join(BASE_DIR, "workflow.log")


def get_logger(name: str) -> logging.Logger:
    """
    Returns a named logger that writes to both the log file and the console.
    Called at the top of each module with the module name so log lines
    are easy to trace back to their source.
    The 'if not logger.handlers' check stops handlers being added
    more than once if the same logger is requested multiple times.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Each log line includes timestamp, module name, level, and the message
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # File handler — pushes log output to workflow.log
        file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
        file_handler.setFormatter(formatter)

        # Console handler — prints to terminal when running locally
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
