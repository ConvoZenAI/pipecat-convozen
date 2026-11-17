# Changelog

All notable changes to **pipecat-convozen** are documented here. This project
follows [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-11-17

### Changed

- `ConvozenHttpTTSService` now uses Ragini 2.0 (`ragini-v2`) by default, with
  `shrajay` as the default voice. Ragini 2.0 voices differ from Ragini v1's, so
  update `voice` when upgrading.
- Text-to-speech languages are now English, Hindi, Kannada, Tamil and Telugu,
  the languages Ragini 2.0 serves.
- The service requests Ragini 2.0's native 48 kHz and resamples to the
  pipeline's output rate. `ragini_v2`, `ragini-2` and `ragini-2.0` are accepted
  as spellings of `ragini-v2`.

### Removed

- Support for `ragini-v1` and `ragini-lite`; `ragini-v2` is the only supported
  model.
- The `speed` setting: Ragini 2.0 does not apply it.

Tested with Pipecat v1.16.0.

## [0.1.0] - 2026-10-07

### Added

- `ConvozenSTTService` for ConvoZen's Akshara speech-to-text models, covering
  nine Indian languages including code-mixed speech. Extends
  `SegmentedSTTService`, so a VAD analyzer is required in the pipeline.
- `ConvozenHttpTTSService` for the Ragini text-to-speech models, streaming audio
  as it is generated.
- Foundational example bot at `examples/foundational/convozen-bot.py`.

Tested with Pipecat v1.12.0.
