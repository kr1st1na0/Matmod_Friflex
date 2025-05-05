import json

def time_to_seconds(time_str):
    """Конвертирует формат 'минуты:секунды.миллисекунды' в секунды."""
    minutes, seconds_millis = time_str.split(":")
    seconds, millis = seconds_millis.split(".")
    return int(minutes) * 60 + int(seconds) + int(millis) / 1000


def get_grouped_moves(json_path):
    """Загружает JSON и возвращает сгруппированный список по ключам."""
    with open(json_path, "r", encoding="utf-8") as file:
        raw_data = json.load(file)

    result = []

    for num_str, entries in raw_data.items():
        num = int(num_str)  # Преобразуем ключ в число
        moves_group = [num]

        for entry in entries:
            move = entry.get("move", "")
            start = time_to_seconds(entry["start_time"])
            end = time_to_seconds(entry["end_time"])
            comment = entry.get("comment", "")
            moves_group.append([move, start, end, comment])

        result.append(moves_group)

    return result