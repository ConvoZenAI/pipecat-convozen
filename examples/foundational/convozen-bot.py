#
# Copyright (c) 2026, ConvoZen
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Voice bot using ConvoZen Akshara for STT and Ragini for TTS.

Run it with:

    uv run examples/foundational/convozen-bot.py

Set CONVOZEN_API_KEY and OPENAI_API_KEY first (a .env file works).
"""

import os

from dotenv import load_dotenv
from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineParams, PipelineWorker
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transcriptions.language import Language
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.transports.daily.transport import DailyParams
from pipecat.workers.runner import WorkerRunner

from pipecat_convozen import ConvozenHttpTTSService, ConvozenSTTService

load_dotenv(override=True)

# Lambdas defer transport parameter creation until the transport is chosen at runtime.
transport_params = {
    "daily": lambda: DailyParams(audio_in_enabled=True, audio_out_enabled=True),
    "webrtc": lambda: TransportParams(audio_in_enabled=True, audio_out_enabled=True),
}


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    """Wire ConvoZen STT and TTS into a voice pipeline and run it."""
    logger.info("Starting bot")

    # One session is shared by every HTTP service and closed when the bot exits.
    import aiohttp

    async with aiohttp.ClientSession() as session:
        stt = ConvozenSTTService(
            api_key=os.environ["CONVOZEN_API_KEY"],
            aiohttp_session=session,
            settings=ConvozenSTTService.Settings(
                language=Language.HI,
                # Akshara handles code-mixed speech; hint both languages.
                lang_tags=["hi", "en"],
            ),
        )

        tts = ConvozenHttpTTSService(
            api_key=os.environ["CONVOZEN_API_KEY"],
            aiohttp_session=session,
            settings=ConvozenHttpTTSService.Settings(
                voice="shrajay",
                language=Language.HI,
            ),
        )

        llm = OpenAILLMService(api_key=os.environ["OPENAI_API_KEY"])

        context = LLMContext(
            [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant in a voice conversation. Your replies "
                        "are spoken aloud, so avoid emojis, bullet points and other "
                        "formatting. Reply to the user in Hindi, briefly."
                    ),
                }
            ]
        )
        # Akshara transcribes complete utterances, so the VAD analyzer marks the
        # boundaries the service needs.
        user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
            context,
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

        worker = PipelineWorker(
            pipeline,
            params=PipelineParams(enable_metrics=True, enable_usage_metrics=True),
        )

        runner = WorkerRunner(handle_sigint=runner_args.handle_sigint)
        await runner.add_workers(worker)

        @transport.event_handler("on_client_connected")
        async def on_client_connected(transport, client):
            logger.info("Client connected")
            context.add_message(
                {"role": "developer", "content": "Please introduce yourself to the user."}
            )
            await worker.queue_frames([LLMRunFrame()])

        @transport.event_handler("on_client_disconnected")
        async def on_client_disconnected(transport, client):
            logger.info("Client disconnected")
            await runner.cancel()

        await runner.run()


async def bot(runner_args: RunnerArguments):
    """Entry point used by the Pipecat runner."""
    transport = await create_transport(runner_args, transport_params)
    await run_bot(transport, runner_args)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
