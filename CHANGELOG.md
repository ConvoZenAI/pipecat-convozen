# Changelog

All notable changes to **pipecat-convozen** are documented here. This project
follows [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-10-07

### Added

- `ConvozenSTTService` for ConvoZen's Akshara speech-to-text models, covering
  nine Indian languages including code-mixed speech. Extends
  `SegmentedSTTService`, so a VAD analyzer is required in the pipeline.
- `ConvozenHttpTTSService` for the Ragini text-to-speech models, streaming audio
  as it is generated.
- Foundational example bot at `examples/foundational/convozen-bot.py`.

Tested with Pipecat v1.12.0.
