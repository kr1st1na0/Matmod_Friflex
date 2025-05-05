from TTS.api import TTS
import torch
import parse_json

json_path = "3067.json"
voice_lang = "en"

# subtitles = parse_json.get_subtitles(json_path)
# start_time = subtitles[0][0] # время начала
# end_time = subtitles[0][1] # время конца
# text = subtitles[0][2]


# grouped_moves = parse_json.get_grouped_moves(json_path)
# target_comment = ""
# flag = False
# for sublist in grouped_moves:
#     for item in sublist[1:]:
#         if item[3] != "":
#             print(item[3])
#             subtitle_text = item[3]
#             flag = True
#             break
#         if (flag): break
#     if (flag): break
target_comment = "The bishop moves to d6, developing a brave move and preparing for the enemy attack"
print(target_comment)

device = "cuda" if torch.cuda.is_available() else "cpu"

# List available 🐸TTS models
print(TTS().list_models())

# Initialize TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
print(tts.speakers)

# Generate voice
tts.tts_to_file(
  text=f"""<speak><prosody rate="x-fast">{target_comment}</prosody></speak>""",
  speaker='Gracie Wise',
  language=voice_lang,
  file_path="audio.wav"
)
