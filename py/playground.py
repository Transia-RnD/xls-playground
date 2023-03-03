#!/usr/bin/env python
# coding: utf-8

import hashlib

from typing import Any, Dict  # noqa: F401

amendment_name: str = 'URIToken'
print(hashlib.sha512(amendment_name.encode("utf-8")).digest().hex().upper()[:64])
