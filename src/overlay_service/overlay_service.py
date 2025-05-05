from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, CompositeAudioClip
import re
import parse_json


# Пути к файлам
video_path = "cutted_video.mp4"
audio_path = "audio.wav"
json_path = "3067.json"
output_path = "final_video.mp4"

def generate_subtitles_by_next_line(text):
    spaces = [m.start() for m in re.finditer(r" ", text)]
    result = []
    last_close = 0
    i = 0
    while last_close < len(text):
        next_pos = (i + 1) * 50
        # Ищем ближайший пробел до next_pos или до конца текста
        candidates = [num for num in spaces if num > last_close and num <= next_pos]
        if not candidates:
            # Если пробелов нет, принудительно разрываем строку
            closest = min(last_close + 50, len(text))
        else:
            closest = candidates[-1]
        result.append(text[last_close:closest].strip())
        last_close = closest
        i += 1
    return "\n".join(result)

# Получаем данные из JSON
subtitles = parse_json.get_grouped_moves(json_path)

start_time = subtitles[0][4][1]
end_time = subtitles[0][7][2]
print(start_time)
print(end_time)


# subtitle_text = ""
#
# for sublist in subtitles:
#     for item in sublist[1:]:
#         if item[3] != "":
#             print(item[3])
#             subtitle_text = item[3]
#             break

subtitle_text = "The bishop moves to d6, developing a brave move and preparing for the enemy attack"
subtitle_text = generate_subtitles_by_next_line(subtitle_text)

ozvuchka = AudioFileClip(audio_path)

# start_time = subtitles[0][0]
# end_audio = subtitles[0][1]
duration = end_time - start_time

# Основное видео
clip = (
    VideoFileClip(video_path)
    .with_start(start_time)
    .with_volume_scaled(0.1) # громкость исходного видео - 10%
    .with_duration(duration)
)
duration = ozvuchka.duration
# Определяем позицию субтитров
_, video_height = clip.size
subtitle_pos = video_height // 2 - 162 - subtitle_text.count('\n') * 40

# Загружаем звуковой файл и синхронизируем его с временем субтитров
audio_clip = (
    AudioFileClip(audio_path)
    .with_start(start_time)        # Начало звука совпадает с началом субтитров
    .with_speed_scaled(1.25)
)
# print(audio_clip.duration)

# Смешиваем оригинальный и новый звук
composite_audio = CompositeAudioClip([clip.audio, audio_clip])

# Создаем клип-субтитры
subtitle_clip = (
    TextClip(
        text=subtitle_text,
        font="arial.ttf",
        font_size=30,
        color="white",
        stroke_color="black",
        stroke_width=2,
        horizontal_align="center",
        vertical_align="center",
        bg_color="black",
        size=(18 * len(subtitle_text), 42 * (1 + subtitle_text.count('\n'))),
    )
    .with_start(start_time)
    .with_duration(duration)
    .with_position(("center", subtitle_pos))
)

# Накладываем субтитры на видео и устанавливаем смешанный звук
final_video = (
    CompositeVideoClip([clip, subtitle_clip])
    .with_audio(composite_audio)
)

# Сохраняем результат
final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
