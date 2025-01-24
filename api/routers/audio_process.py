import os

from deps import deepgram_client, deepgram_config, openai_client
from fastapi import APIRouter, File, UploadFile

router = APIRouter(tags=["Audio processing"], prefix="/audio")


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...), language: str = "pt"):
    # Leitura e gravação do arquivo
    audio_content: bytes = file.file.read()
    audio_dir = "../audios_temp"
    audio_path = os.path.join(audio_dir, "audio.wav")

    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)

    with open(audio_path, "wb") as f:
        f.write(audio_content)

    # Usando o arquivo para transcrição
    with open(audio_path, "rb") as audio_file:
        payload = {"buffer": audio_file}
        options = deepgram_config
        transcription = deepgram_client.listen.prerecorded.v("1").transcribe_file(payload, options)  # type: ignore

        # USING OPENAI WHISPER TO MAKE TRANSCRIPTION
        # try:
        #     transcription = openai_client.audio.transcriptions.create(
        #         model="whisper-1",
        #         file=audio_file,
        #         language=language
        #     )
        # except Exception as e:
        #     return {"error": str(e)}

    os.remove(audio_path)

    return {"transcription": transcription["results"]["channels"][0]["alternatives"][0]["transcript"]}  # type: ignore
