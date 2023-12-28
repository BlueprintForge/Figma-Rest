import logging
from logging_setup import setup_logging


def main():
    setup_logging()
    logging.debug("Starting script")


if __name__ == "__main__":
    main()
