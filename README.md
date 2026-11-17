# pipecat-convozen

Pipecat services for [ConvoZen](https://convozen.ai/)'s speech models: **Akshara**
for speech-to-text and **Ragini** for text-to-speech.

Akshara transcribes nine Indian languages — Bengali, English, Gujarati, Hindi,
Kannada, Malayalam, Marathi, Tamil and Telugu — including code-mixed speech.
Ragini 2.0 speaks English, Hindi, Kannada, Tamil and Telugu. ConvoZen's
research write-ups describe the models:
[Akshara](https://convozen.ai/research/article/akshara) and
[Ragini](https://convozen.ai/research/article/ragini).

> A community integration, maintained by [ConvoZen](https://convozen.ai/) —
> not by the Pipecat team. Please report issues here rather than on the Pipecat
> repository.

| Service | Class | Base class |
| --- | --- | --- |
| Speech-to-text | `ConvozenSTTService` | `SegmentedSTTService` |
| Text-to-speech | `ConvozenHttpTTSService` | `TTSService` |

## Installation

```bash
uv add pipecat-convozen
```

## Prerequisites

An API key from [ConvoZen](https://app.convozen.ai/developers/models), set as
`CONVOZEN_API_KEY`.

## Usage

Akshara transcribes one complete utterance per request and emits no interim
results, so **a VAD analyzer is required** in the pipeline to mark utterance
boundaries. Both services take the bot's shared `aiohttp` session.

```python
import aiohttp
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.transcriptions.language import Language

from pipecat_convozen import ConvozenHttpTTSService, ConvozenSTTService

async with aiohttp.ClientSession() as session:
    stt = ConvozenSTTService(
        api_key=os.environ["CONVOZEN_API_KEY"],
        aiohttp_session=session,
        settings=ConvozenSTTService.Settings(
            language=Language.HI,
            lang_tags=["hi", "en"],  # code-mixed Hindi and English
        ),
    )

    tts = ConvozenHttpTTSService(
        api_key=os.environ["CONVOZEN_API_KEY"],
        aiohttp_session=session,
        settings=ConvozenHttpTTSService.Settings(voice="shrajay", language=Language.HI),
    )

    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        LLMContext(),
        user_params=LLMUserAggregatorParams(vad_analyzer=SileroVADAnalyzer()),
    )

    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            user_aggregator,
            llm,
            tts,
            transport.output(),
            assistant_aggregator,
        ]
    )
```

### Speech-to-text settings

| Setting | Type | Default | Description |
| --- | --- | --- | --- |
| `model` | `str` | `"akshara-pro"` | `"akshara-pro"` or the base `"akshara"` |
| `language` | `Language \| str` | `Language.EN` | Language of the audio; also supplies the default hint |
| `lang_tags` | `list[str]` | `None` | Language hints, e.g. `["hi", "en"]` for code-mixed speech |
| `keywords` | `list[str]` | `None` | Domain words to bias recognition towards |
| `blank_penalty` | `float` | `None` | Penalizes blank/silence tokens; unbounded |
| `word_timestamps` | `bool` | `False` | Request per-word timings |

Akshara returns a `score` with each transcript. It is an unbounded
log-probability, closer to zero being better, not a `[0, 1]` confidence, and it is
available on the `TranscriptionFrame` `result` payload.

### Text-to-speech settings

| Setting | Type | Default | Description |
| --- | --- | --- | --- |
| `model` | `str` | `"ragini-v2"` | `"ragini-v2"` (Ragini 2.0), currently the only supported model |
| `voice` | `str` | `"shrajay"` | A voice for the chosen model and language (below) |
| `language` | `Language \| str` | `Language.EN` | `en`, `hi`, `kn`, `ta` or `te` |

Ragini 2.0 voices depend on the language:

| Languages | Voices |
| --- | --- |
| `en`, `hi` | `shrajay` (default), `siddharth`, `parmi`, `sherin`, `bhavya`, `shreya` |
| `kn`, `ta`, `te` | `amaya`, `parmi`, `roohi`, `bhavya`, `shrajay`, `siddharth` |

An unknown voice name is not an error — the API returns an arbitrary voice — so
check the spelling. Ragini 2.0 has no speaking-rate control.

Ragini 2.0 always returns 48 kHz audio; it is resampled to the pipeline's output
rate automatically. Audio streams back as it
is generated, which keeps time-to-first-audio down.

Both services accept `base_url=` to reach a self-hosted ConvoZen deployment.

## Running the example

[`examples/foundational/convozen-bot.py`](examples/foundational/convozen-bot.py)
is a complete voice bot. It needs `CONVOZEN_API_KEY` and `OPENAI_API_KEY`:

```bash
uv sync --extra example
uv run examples/foundational/convozen-bot.py
```

Then open the URL it prints and start talking. Pass `-t daily` to use Daily
instead of the default WebRTC transport.

## Tests

```bash
uv sync --extra dev
uv run pytest
```

The tests are hermetic — they use a fake `aiohttp` session, so no API key and no
network access are needed.

## Compatibility

Tested with **Pipecat v1.16.0**.

## License

BSD 2-Clause. See [LICENSE](LICENSE).
