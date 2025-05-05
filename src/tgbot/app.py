import os
from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
import logging # Добавляем импорт для логирования

# Настройка Flask
app = Flask(__name__)
app.secret_key = 'your_secret_key_here' # Секретный ключ для flash сообщений
# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Папка для сохранения загруженных файлов
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Создать папку uploads, если она не существует
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Снять ограничение на размер загружаемых файлов (будьте осторожны!)
# Flask по умолчанию ограничивает размер тела запроса.
# Можно установить None для неограниченного размера, но это опасно.
# Лучше установить очень большое число, если нужно снять стандартное ограничение.
# Например, 1000 МБ (1000 * 1024 * 1024 байт)
# app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024 # 1000 МБ
# Для полного снятия ограничения (опасно):
app.config['MAX_CONTENT_LENGTH'] = None

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {'mp4', 'json'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    logging.info("Received POST request to /upload")

    # Проверка наличия обоих файлов в запросе
    if 'video_file' not in request.files or 'json_file' not in request.files:
        logging.warning("Missing video_file or json_file in request.")
        # Возвращаем статус 400 Bad Request и сообщение об ошибке
        return {'error': 'Оба файла (видео и JSON) обязательны для загрузки.'}, 400

    video_file = request.files['video_file']
    json_file = request.files['json_file']

    # Если пользователь не выбрал файл (хотя бот должен это гарантировать)
    if video_file.filename == '' or json_file.filename == '':
        logging.warning("Empty filename for video_file or json_file.")
        return {'error': 'Оба файла должны быть выбраны.'}, 400

    # Проверка расширений файлов (на стороне сервера)
    if not video_file.filename.lower().endswith('.mp4') or not json_file.filename.lower().endswith('.json'):
        logging.warning(f"Invalid file extensions: video={video_file.filename}, json={json_file.filename}")
        return {'error': 'Недопустимый формат файла. Разрешены только MP4 и JSON.'}, 400

    # Если оба файла выбраны и имеют правильные расширения
     # Безопасное получение имени файла
    video_filename = secure_filename(video_file.filename)
    json_filename = secure_filename(json_file.filename)

    # Добавляем что-то уникальное к имени файла, чтобы избежать коллизий
    # Например, timestamp или id пользователя (если он передается)
    # Для простоты пока используем оригинальное имя, но в продакшене это плохо
    # video_filename = f"{uuid.uuid4()}_{video_filename}" # Пример с UUID
    # json_filename = f"{uuid.uuid4()}_{json_filename}" # Пример с UUID

    # Пути для сохранения файлов
    video_filepath = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
    json_filepath = os.path.join(app.config['UPLOAD_FOLDER'], json_filename)
    try:
        video_file.save(video_filepath)
        json_file.save(json_filepath)
        logging.info(f"Files successfully saved: video={video_filepath}, json={json_filepath}")

        # Здесь вы можете добавить логику для дальнейшей обработки файлов
        # Например, запустить отдельный процесс или добавить задачу в очередь

        # Возвращаем успешный ответ
        return {'message': 'Файлы успешно загружены!'}, 200
    except Exception as e:
        logging.error(f'Произошла ошибка при сохранении файлов: {e}', exc_info=True)
        # Возможно, стоит удалить уже сохраненный файл, если другой не удалось сохранить
        if os.path.exists(video_filepath):
            os.remove(video_filepath)
        if os.path.exists(json_filepath):
             os.remove(json_filepath)
        # Возвращаем статус 500 Internal Server Error
        return {'error': f'Произошла ошибка при сохранении файлов: {e}'}, 500

    # Этот код не должен достигаться, если все проверки прошли
    # return {'error': 'Неизвестная ошибка'}, 500 # Лучше вернуть ошибку, если сюда попали
    

if __name__ == '__main__':
    # Запуск веб-сервера. debug=True только для разработки!
    # Для продакшена используйте более надежный веб-сервер (например, Gunicorn или uWSGI)
    # Важно: Если бот и веб-сервер на разных машинах, нужно указать host='0.0.0.0'
    # Но будьте осторожны, открывая сервер в интернет без должной защиты.
    app.run(debug=True)