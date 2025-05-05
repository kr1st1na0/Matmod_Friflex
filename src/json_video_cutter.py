import subprocess
import os
import json

def parse_time(time_str):
    """Конвертирует время в формате MM:SS.mmm в секунды с миллисекундами"""
    try:
        minutes, rest = time_str.split(':')
        seconds, milliseconds = rest.split('.')
        total_seconds = int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000
        return total_seconds
    except ValueError:
        print(f"Ошибка: неверный формат времени {time_str}")
        return None

def process_timestamps(json_file):
    """Обрабатывает JSON файл с временными метками"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        segments = []
        total_duration = 0
        for move in data:
            start = parse_time(move['start_time'])
            end = parse_time(move['end_time'])
            if start is not None and end is not None and start < end:
                duration = end - start
                total_duration += duration
                segments.append((start, end))
                print(f"Найден отрезок: {move['start_time']}-{move['end_time']} ({duration:.3f} секунд)")
        
        print(f"\nОбщая длительность всех отрезков: {total_duration:.3f} секунд")
        if not segments:
            print("Ошибка: не найдены корректные временные отрезки в JSON файле")
            return None
        
        return segments
    except Exception as e:
        print(f"Ошибка при обработке файла {json_file}: {str(e)}")
        return None

def cut_video(input_file, segments):
    """Обрезает видео по указанным отрезкам"""
    if not os.path.exists(input_file):
        print(f"Ошибка: файл {input_file} не найден")
        return None
    
    # Создаем временную директорию, удаляя старую если она существует
    if os.path.exists("temp_cuts"):
        import shutil
        shutil.rmtree("temp_cuts")
    os.makedirs("temp_cuts")
    
    cut_files = []
    
    # Обрезаем каждый отрезок
    for i, (start, end) in enumerate(segments):
        output_file = f"temp_cuts/cut_{i}.mp4"
        duration = end - start
        
        # Обрезаем видео с точным указанием времени
        command = [
            'ffmpeg',
            '-y',  # Автоматически подтверждаем перезапись файлов
            '-i', input_file,
            '-ss', f"{start:.3f}",  # Указываем время с миллисекундами
            '-t', f"{duration:.3f}",  # Указываем длительность с миллисекундами
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-avoid_negative_ts', '1',
            output_file
        ]
        print(f"Обработка отрезка {i+1}: {start:.3f} - {end:.3f} секунд")
        subprocess.run(command, check=True)
        cut_files.append(output_file)
    
    return cut_files

def merge_videos(input_files, output_file="output.mp4"):
    """Склеивает видео из списка файлов"""
    # Создаем список файлов для склейки
    with open("temp_cuts/file_list.txt", "w") as f:
        for file in input_files:
            f.write(f"file '{os.path.basename(file)}'\n")
    
    # Склеиваем видео с более точными настройками
    command = [
        'ffmpeg',
        '-y',  # Автоматически подтверждаем перезапись файлов
        '-f', 'concat',
        '-safe', '0',
        '-i', 'temp_cuts/file_list.txt',
        '-c:v', 'libx264',  # Используем кодирование вместо копирования
        '-c:a', 'aac',
        '-preset', 'ultrafast',  # Используем быстрое кодирование
        '-crf', '23',  # Качество видео
        '-vsync', '0',  # Точная синхронизация кадров
        '-copyts',  # Сохраняем оригинальные временные метки
        output_file
    ]
    print("Склеиваем отрезки...")
    subprocess.run(command, check=True)
    
    # Очищаем временные файлы
    for file in input_files:
        os.remove(file)
    os.remove("temp_cuts/file_list.txt")
    os.rmdir("temp_cuts")
    
    return output_file

def process_video(video_file, json_file, output_file="output.mp4"):
    """Основная функция обработки видео"""
    print("=== Обработка видео по JSON ===")
    
    # Проверяем существование файлов
    if not os.path.exists(video_file):
        print(f"Ошибка: видео файл {video_file} не найден")
        return False
    
    if not os.path.exists(json_file):
        print(f"Ошибка: JSON файл {json_file} не найден")
        return False
    
    # Обрабатываем временные метки
    print("\nАнализируем временные метки...")
    segments = process_timestamps(json_file)
    if not segments:
        return False
    
    # Обрезаем видео
    print("\nНачинаем обрезку видео...")
    cut_files = cut_video(video_file, segments)
    if not cut_files:
        return False
    
    # Склеиваем видео
    print("\nСклеиваем отрезки...")
    final_output = merge_videos(cut_files, output_file)
    print(f"\nГотово! Видео сохранено как: {final_output}")
    return True

if __name__ == "__main__":
    print("=== Обработка видео по JSON ===")
    
    # Запрашиваем у пользователя пути к файлам
    video_file = input("Введите путь к видео файлу (например: 3067.mp4): ").strip()
    json_file = input("Введите путь к JSON файлу с временными метками (например: timestamps.json): ").strip()
    output_file = input("Введите имя выходного файла (например: output.mp4): ").strip()
    
    # Если пользователь не ввел имя выходного файла, используем значение по умолчанию
    if not output_file:
        output_file = "output.mp4"
    
    # Обрабатываем видео
    process_video(video_file, json_file, output_file) 