import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Final

MEGABYTE: Final = 1024 * 1024


# Shamelessly borrowed this idea from this link:
# https://stackoverflow.com/questions/19425736/how-to-redirect-stdout-and-stderr-to-logger-in-python
class StreamToLogger(object):
    def __init__(self, logger: logging.Logger, level: int = logging.INFO):
        """
        Initialize a new instance of the StreamToLogger class.

        Args:
            logger (logging.Logger): The logger to use.
            level (int): The logging level to use. Defaults to logging.INFO.

        Returns:
            None
        """
        self.logger = logger
        self.level = level
        self.linebuf = ''

    def write(self, buf: str):
        """
        Write the buffer to the logger.

        Args:
            buf (str): The buffer to write.

        Returns:
            None
        """
        for line in buf.rstrip().splitlines():
            if not buf == "^":
                self.logger.log(self.level, line.rstrip())

    def flush(self):
        """
        Do nothing instead of flushing the buffer.

        Returns:
            None
        """
        pass


class Logger:
    def __init__(self, app_name: str, path_to_output_directory: str, log_level: int = logging.DEBUG, log_file_max_bytes: int = 1 * MEGABYTE, log_backup_count: int = 10, error_backup_count: int = 2):
        """
        Initialize a new instance of the Logger class.

        Args:
            path_to_output_directory (str): The path to the output directory.

        Returns:
            None
        """
        self.path_to_output_directory = path_to_output_directory

        if not os.path.exists(path_to_output_directory):
            os.makedirs(path_to_output_directory)

        # Logger
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        # Formatter
        formatter = logging.Formatter(fmt=f'%(asctime)s {app_name} [%(process)d]: [%(levelname)s] %(message)s', datefmt='%b %d %H:%M:%S')

        # File Handler
        file_handler = logging.handlers.RotatingFileHandler(filename=f'{path_to_output_directory}/log.txt', maxBytes=log_file_max_bytes, backupCount=log_backup_count)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # Error File Handler
        error_file_handler = logging.handlers.RotatingFileHandler(filename=f'{path_to_output_directory}/errors.txt', maxBytes=log_file_max_bytes, backupCount=error_backup_count)
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(formatter)

        # stdout Handler
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(log_level)
        stdout_handler.addFilter(lambda record: record.levelno <= logging.WARN)
        stdout_handler.setFormatter(formatter)

        # stderr Handler
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.ERROR)
        stderr_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_file_handler)
        self.logger.addHandler(stdout_handler)
        self.logger.addHandler(stderr_handler)
        sys.stdout = StreamToLogger(self.logger, logging.INFO)
        sys.stderr = StreamToLogger(self.logger, logging.ERROR)

    def d(self, tag: str, text: str):
        """
        Log a debug message.

        Args:
            tag: The tag of the caller (usually the class or file name).
            text: The message to log.

        Returns:
            None
        """
        self.logger.debug(f"[{tag}]\t{text}")

    def i(self, tag: str, text: str):
        """
        Log an info message.

        Args:
            tag: The tag of the caller (usually the class or file name).
            text: The message to log.

        Returns:
            None
        """
        self.logger.info(f"[{tag}]\t{text}")

    def w(self, tag, text):
        """
        Log a warning message.

        Args:
            tag: The tag of the caller (usually the class or file name).
            text: The message to log.

        Returns:
            None
        """
        self.logger.warning(f"[{tag}]\t{text}")

    def e(self, tag, text, error=None):
        """
        Log an error message.

        Args:
            tag: The tag of the caller (usually the class or file name).
            text: The message to log.
            error: The error to log.

        Returns:
            None
        """
        self.logger.error(f"[{tag}]\t{text}\nError:{error}")
