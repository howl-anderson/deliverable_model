# -*- coding: utf-8 -*-

"""Top-level package for deliverable_model."""

__author__ = """Xiaoquan Kong"""
__email__ = "u1mail2me@gmail.com"
__version__ = "0.6.3"

import logging

import deliverable_model.serving  # for auto registry

from deliverable_model.serving import load, make_request, make_endpoint_config
from deliverable_model.get_metadata import get_metadata

# setup logging
logger = logging.getLogger(__name__)
console_formater = logging.Formatter(logging.BASIC_FORMAT)
console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formater)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)
