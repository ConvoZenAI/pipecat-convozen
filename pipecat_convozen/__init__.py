#
# Copyright (c) 2026, ConvoZen
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Pipecat services for ConvoZen's Akshara speech-to-text and Ragini text-to-speech."""

from pipecat_convozen.stt import (
    CONVOZEN_TTFS_P99,
    ConvozenSTTService,
    ConvozenSTTSettings,
)
from pipecat_convozen.tts import (
    ConvozenHttpTTSService,
    ConvozenHttpTTSSettings,
)

__version__ = "0.2.1"

__all__ = [
    "CONVOZEN_TTFS_P99",
    "ConvozenHttpTTSService",
    "ConvozenHttpTTSSettings",
    "ConvozenSTTService",
    "ConvozenSTTSettings",
    "__version__",
]
