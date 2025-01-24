from config import settings
from deepgram import DeepgramClient, PrerecordedOptions
from openai import AsyncOpenAI

openai_client = AsyncOpenAI(api_key=settings.OPENAI_KEY)
deepgram_client = DeepgramClient(settings.DEEPGRAM_KEY)
deepgram_config = PrerecordedOptions(punctuate=False, model="nova-2", language="pt-BR")
