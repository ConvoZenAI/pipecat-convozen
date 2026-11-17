#
# Copyright (c) 2024-2026, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import pytest
from pipecat.transcriptions.language import Language

from pipecat_convozen.tts import (
    ConvozenHttpTTSService,
    ConvozenHttpTTSSettings,
    language_to_convozen_language,
)


def _service(sample_rate: int | None = None, **settings) -> ConvozenHttpTTSService:
    service = ConvozenHttpTTSService.__new__(ConvozenHttpTTSService)
    service._settings = ConvozenHttpTTSSettings(
        model="ragini-v2",
        voice="shrajay",
        language="en",
    )
    for key, value in settings.items():
        setattr(service._settings, key, value)
    service._sample_rate = sample_rate
    return service


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        (Language.EN, "en"),
        (Language.HI, "hi"),
        (Language.TA_IN, "ta"),
        (Language.ML_IN, None),
        (Language.MR, None),
        (Language.DE, None),
    ],
)
def test_language_maps_to_two_letter_code(language, expected):
    assert language_to_convozen_language(language) == expected


def test_requests_model_native_rate():
    assert _service()._request_sample_rate() == 48000


def test_pipeline_rate_does_not_change_request_rate():
    # Ragini 2.0 always returns 48 kHz; Pipecat resamples from the WAV header.
    assert _service(sample_rate=8000)._request_sample_rate() == 48000


@pytest.mark.parametrize(
    ("model", "wire"),
    [
        ("ragini-v2", "ragini-v2"),
        ("ragini_v2", "ragini-v2"),
        ("Ragini-2.0", "ragini-v2"),
    ],
)
def test_model_aliases_map_to_wire_name(model, wire):
    assert _service(model=model)._build_body("hi")["model"] == wire


def test_body_uses_speaker_not_voice():
    body = _service()._build_body("hello")
    assert body["speaker"] == "shrajay"
    assert "voice" not in body


def test_body_has_no_format_field():
    # The endpoint has no format field; output is always WAV.
    assert "format" not in _service()._build_body("hello")


def test_body_fields():
    service = _service(language="hi", voice="sherin")
    assert service._build_body("नमस्ते") == {
        "text": "नमस्ते",
        "language": "hi",
        "speaker": "sherin",
        "model": "ragini-v2",
        "sample_rate": "48000",
        "stream": "true",
    }
