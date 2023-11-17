# -*- coding: utf-8 -*-

"""
Configuration file for the whole project
"""
import os
import logging
from pathlib import Path


logging.basicConfig(
    # format='%(message)s',
    format='%(filename)s [LINE:%(lineno)d]\t[%(asctime)s] %(levelname)-s\t%(funcName)s() \t\t%(message)s',
    level=logging.INFO,
    datefmt="%y-%m-%d %H:%M:%S")

log = logging.getLogger(__name__)

EN = "en"
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", EN)
DEFAULT_STYLE = os.getenv("DEFAULT_STYLE", "ultra")

HTML_EXPORT_DIRECTORY_PATH_LOCAL = os.environ.get("HTML_EXPORT_DIRECTORY_PATH_LOCAL", "")
# TODO Add current directory as Default

if HTML_EXPORT_DIRECTORY_PATH_LOCAL:
    Path(HTML_EXPORT_DIRECTORY_PATH_LOCAL).mkdir(parents=True, exist_ok=True)
