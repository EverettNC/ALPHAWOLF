# © 2025 The Christman AI Project. All rights reserved.
#
# This code is released as part of a trauma-informed, dignity-first AI ecosystem
# designed to protect, empower, and elevate vulnerable populations.
#
# By using, modifying, or distributing this software, you agree to uphold the following:
# 1. Truth — No deception, no manipulation.
# 2. Dignity — Respect the autonomy and humanity of all users.
# 3. Protection — Never use this to exploit or harm vulnerable individuals.
# 4. Transparency — Disclose all modifications and contributions clearly.
# 5. No Erasure — Preserve the mission and ethical origin of this work.
#
# This is not just code. This is redemption in code.
# Contact: lumacognify@thechristmanaiproject.com
# https://thechristmanaiproject.com
"""Middleware utilities for AlphaWolf Dashboard API."""

import logging
from typing import Callable
from flask import Request

logger = logging.getLogger(__name__)


def request_logger_middleware(handler: Callable):
    """Log incoming requests before passing to handler."""

    def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request")  # type: ignore
        if request:
            logger.info("Incoming %s %s", request.method, request.path)
        return handler(*args, **kwargs)

    return wrapper
