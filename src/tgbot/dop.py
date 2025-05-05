import telebot
from telebot import types
import os
import json

# Убедитесь, что переменная окружения API_TOKEN установлена
token = os.getenv("API_TOKEN")

if not token:
    print("Error: API_TOKEN environment variable not set.")
    exit()

bot = telebot.TeleBot(token)

# --- Глобальные переменные ---
user_styles = {}
user_interface_languages = {}  # Для хранения языка интерфейса
user_processing_languages = {}  # Для хранения языка обработки
# user_changing_interface_lang = {} # Этот флаг больше не нужен, используем user_state
user_state = {} # Добавляем словарь для хранения состояния пользователя
user_previous_state = {} # Добавляем словарь для хранения ПРЕДЫДУЩЕГО состояния пользователя

# Директории для сохранения файлов
VIDEO_DIR = "user_videos"
JSON_DIR = "user_json" # Добавляем директорию для JSON

# Создаем директории, если они не существуют
if not os.path.exists(VIDEO_DIR):
    os.makedirs(VIDEO_DIR)
if not os.path.exists(JSON_DIR):
    os.makedirs(JSON_DIR)

# --- Константы для состояний пользователя ---
STATE_AWAITING_INTERFACE_LANG = 'awaiting_interface_lang'
STATE_AWAITING_STYLE = 'awaiting_style'
STATE_AWAITING_PROCESSING_LANG = 'awaiting_processing_lang'
STATE_AWAITING_VIDEO = 'awaiting_video'
STATE_AWAITING_JSON = 'awaiting_json'
STATE_PROCESSING = 'processing'
STATE_IDLE = 'idle' # Возможно, конечное состояние после обработки

# --- Тексты на разных языках ---
texts = {
    'en': {
        'welcome': "Welcome!\n\n"
                    "❔ What the bot does:\n\n"
                       "🔊 Adds professional voice acting and subtitles in 5 languages 🌍 (Russian, English, Chinese, Spanish, Hindi)\n"
                       "💻 Retains all original elements (players, chessboard, and music)\n"
                       "🎵 Highlights the key moments of the party with perfect synchronization\n"
                       "🎥 Converts them into vertical videos optimized for YouTube Shorts 📱\n\n"
                       "🎯 Result:\n"
                       "Dynamic, informative and stylishly designed videos, ready for publication!\n\n"
                       "🎮 How it works:\n\n"
                       "🗣️ Select the interface language\n"
                       "🎨 Define the processing style:\n"
                       "Educational (detailed analysis with an emphasis on tactics) or Entertaining (memes, effects and humorous accompaniment)\n"
                       "🔊 Specify the language for subtitles and voiceover\n"
                       "📤 Download the original video\n\n"
                       "1⃣ To start, select the interface language:",
        'start_button': "🟢 Getting started with the bot",
        'select_interface_language': "Please select your preferred interface language:",
        'interface_language_selected': "Interface language set to: {language}",
        'style_selection': "Great! Now choose the processing style:",
        'educational_style': "📘 Educational style (Deep analysis)",
        'funny_style': "🎭 Entertaining style (Memes and humor)",
        'style_selected': "The learning style is selected. Great!",
        'funny_style_selected': "An entertaining style has been chosen. We are preparing memes!",
        'select_processing_language': "Now choose the language for subtitles and voiceover:",
        'processing_language_selected': "The processing language is set to {language}.",
        'upload_video_prompt': "Perfect! Now upload your chess game video file:",
        'upload_video_button': "⬆️ Upload video file", # Кнопка осталась в текстах, но не будет использоваться в клавиатуре
        'video_received': "🎥 Video received. Now please upload the JSON file with the game data.",
        'upload_json_prompt': "Please upload the JSON file with the game data.",
        'upload_json_button': "📄 Upload JSON file",
        'json_received': "📄 JSON file received. Starting processing...",
        'follow_instructions': "Please follow the instructions. Send the requested file type.",
        'select_action': "Select an action:",
        'invalid_input': "Please use the buttons or commands to interact.",
        'bot_description': "I will add voice acting and subtitles in your chosen language!",
        'processing_started': "Your video and JSON data are being processed. This may take some time...",
        'invalid_file_type': "Invalid file type. Please upload a {expected_type} file.",
        'json_error': "Error reading the JSON file. Please ensure it's a valid JSON.",
         'video_note_not_allowed': "Video notes are not supported. Please upload a regular video file.",
        # --- Тексты для команд меню ---
        'command_instruction_desc': "Show bot instructions",
        'command_change_interface_lang_desc': "Change interface language",
        'command_change_processing_lang_desc': "Change subtitle/voiceover language",
        'command_change_style_desc': "Change processing style",
        'description': "❔ What the bot does:\n\n"
                       "🔊 Adds professional voice acting and subtitles in 5 languages 🌍 (Russian, English, Chinese, Spanish, Hindi)\n"
                       "💻 Retains all original elements (players, chessboard, and music)\n"
                       "🎵 Highlights the key moments of the party with perfect synchronization\n"
                       "🎥 Converts them into vertical videos optimized for YouTube Shorts 📱\n\n"
                       "🎯 Result:\n"
                       "Dynamic, informative and stylishly designed videos, ready for publication!\n\n"
                       "🎮 How it works:\n\n"
                       "🗣️ Select the interface language\n"
                       "🎨 Define the processing style:\n"
                       "Educational (detailed analysis with an emphasis on tactics) or Entertaining (memes, effects and humorous accompaniment)\n"
                       "🔊 Specify the language for subtitles and voiceover\n"
                       "📤 Download the original video\n\n"
    },
    'ru': {
        'welcome': "Добро пожаловать!\n\n"
                    "❔ Что делает бот:\n\n"
                       "🔊 добавляет профессиональную озвучку и субтитры на 5 языках 🌍 (русский, английский, китайский, испанский, хинди)\n"
                       "💻 сохраняет все оригинальные элементы (игроков, шахматную доску и музыку)\n"
                       "🎵 выделяет ключевые моменты партии с идеальной синхронизацией\n"
                       "🎥 преобразует в вертикальные ролики оптимизированные для YouTube Shorts 📱\n\n"
                       "🎯 Результат:\n"
                       "динамичные, информативные и стильно оформленные видео, готовые к публикации!\n\n"
                       "🎮 Как это работает:\n\n"
                       "🗣️ выберите язык интерфейса\n"
                       "🎨 определите стиль обработки:\n"
                       "обучающий (детальный анализ с акцентами на тактике) или развлекательный (мемы, эффекты и юмористическое сопровождение)\n"
                       "🔊 укажите язык для субтитров и озвучки\n"
                       "📤 загрузите исходное видео\n\n"
                       "1⃣ Для начала выберите язык интерфейса:",
        'start_button': "🟢 Начать работу с ботом",
        'select_interface_language': "Пожалуйста, выберите предпочитаемый язык интерфейса:",
        'interface_language_selected': "Язык интерфейса установлен на: {language}.",
        'style_selection': "Отлично! Теперь выберите стиль обработки:",
        'educational_style': "📘 Обучающий стиль (Глубокий анализ)",
        'funny_style': "🎭 Развлекательный стиль (Мемы и юмор)",
        'style_selected': "Выбран обучающий стиль. Отлично!",
        'funny_style_selected': "Выбран развлекательный стиль. Готовим мемы!",
        'select_processing_language': "Теперь выберите язык для субтитров и озвучки:",
        'processing_language_selected': "Язык обработки установлен на: {language}.",
        'upload_video_prompt': "Отлично! Теперь загрузите видео файл шахматной партии:",
        'upload_video_button': "⬆️ Загрузить видео файл", # Кнопка осталась в текстах, но не будет использоваться в клавиатуре
        'video_received': "🎥 Видео получено. Теперь, пожалуйста, загрузите JSON файл с данными партии.",
        'upload_json_prompt': "Пожалуйста, загрузите JSON файл с данными партии.",
        'upload_json_button': "📄 Загрузить JSON файл",
        'json_received': "📄 JSON файл получен. Начинаю обработку...",
        'follow_instructions': "Пожалуйста, следуйте инструкциям. Отправьте запрошенный тип файла.",
        'select_action': "Выберите действие:",
        'invalid_input': "Пожалуйста, используйте кнопки или команды для взаимодействия.",
        'bot_description': "Я добавлю озвучку и субтитры на выбранном вами языке!",
        'processing_started': "Ваше видео и данные JSON обрабатываются. Это может занять некоторое время...",
        'invalid_file_type': "Неверный тип файла. Пожалуйста, загрузите файл типа {expected_type}.",
        'json_error': "Ошибка при чтении JSON файла. Пожалуйста, убедитесь, что это валидный JSON.",
        'video_note_not_allowed': "Кружки не поддерживаются. Пожалуйста, загрузите обычный видеофайл.",
        # --- Тексты для команд меню ---
        'command_instruction_desc': "Показать инструкцию бота",
        'command_change_interface_lang_desc': "Изменить язык интерфейса",
        'command_change_processing_lang_desc': "Изменить язык субтитров/озвучки",
        'command_change_style_desc': "Изменить стиль обработки",
        'description': "❔ Что делает бот:\n\n"
                       "🔊 добавляет профессиональную озвучку и субтитры на 5 языках 🌍 (русский, английский, китайский, испанский, хинди)\n"
                       "💻 сохраняет все оригинальные элементы (игроков, шахматную доску и музыку)\n"
                       "🎵 выделяет ключевые моменты партии с идеальной синхронизацией\n"
                       "🎥 преобразует в вертикальные ролики оптимизированные для YouTube Shorts 📱\n\n"
                       "🎯 Результат:\n"
                       "динамичные, информативные и стильно оформленные видео, готовые к публикации!\n\n"
                       "🎮 Как это работает:\n\n"
                       "🗣️ выберите язык интерфейса\n"
                       "🎨 определите стиль обработки:\n"
                       "обучающий (детальный анализ с акцентами на тактике) или развлекательный (мемы, эффекты и юмористическое сопровождение)\n"
                       "🔊 укажите язык для субтитров и озвучки\n"
                       "📤 загрузите исходное видео\n\n"
    },
     'es': {
        'welcome': "¡Bienvenido!\n\n"
                    "❔ Lo que hace el bot:\n\n"
                       "🔊 agrega la formación profesional de los doblajes y subtítulos en 5 idiomas 🌍 (ruso, inglés, chino, español, hindi)\n"
                       "💻 conserva todos los elementos originales (jugadores, tablero de ajedrez y la música)\n"
                       "🎵 resalta los momentos clave del partido con una perfecta sincronización\n"
                       "🎥 convierte en verticales de rodillos optimizado para YouTube Shorts 📱\n\n"
                       "🎯 Resultado:\n"
                       "dinámicos, informativos y elegantes, vídeo, listos para su publicación!\n\n"
                       "🎮 Cómo funciona:\n\n"
                       "🗣️ seleccione el idioma de la interfaz\n"
                       "🎨 defina el estilo de procesamiento:\n"
                       "educativo (análisis detallado con énfasis en tácticas) o entretenido (memes, efectos y acompañamiento humorístico)\n"
                       "🔊 especifique el idioma para los Subtítulos y la actuación de voz\n"
                       "📤 descargue el video original\n\n"
                       "1⃣ To start, select the interface language:",
        'start_button': "🟢 Empezar a usar el bot",
        'select_interface_language': "Por favor, selecciona tu idioma de interfaz preferido:",
        'interface_language_selected': "Idioma de interfaz configurado a: {language}.",
        'style_selection': "¡Genial! Ahora elige el estilo de procesamiento:",
        'educational_style': "📘 Estilo educativo (Análisis profundo)",
        'funny_style': "🎭 Estilo entretenido (Memes y humor)",
        'style_selected': "Se ha seleccionado el estilo educativo. ¡Excelente!",
        'funny_style_selected': "Se ha seleccionado el estilo entretenido. ¡Estamos preparando memes!",
        'select_processing_language': "Ahora elige el idioma para los subtítulos y la narración:",
        'processing_language_selected': "El idioma de procesamiento se ha configurado a: {language}.",
        'upload_video_prompt': "¡Perfecto! Ahora sube el archivo de video de tu partida de ajedrez:",
        'upload_video_button': "⬆️ Subir archivo de video", # Кнопka осталась в текстах, но не будет использоваться в клавиатуре
        'video_received': "🎥 Video recibido. Ahora, por favor, sube el archivo JSON con los datos de la partida.",
        'upload_json_prompt': "Por favor, sube el archivo JSON con los datos de la partida.",
        'upload_json_button': "📄 Subir archivo JSON",
        'json_received': "📄 Archivo JSON recibido. Iniciando procesamiento...",
        'follow_instructions': "Por favor, sigue las instrucciones. Envía el tipo de archivo solicitado.",
        'select_action': "Selecciona una acción:",
        'invalid_input': "Por favor, usa los botones o comandos para interactuar.",
        'bot_description': "¡Añadiré narración y subtítulos en el idioma que elijas!",
        'processing_started': "Tu video y datos JSON están siendo procesados. Esto puede tomar algún tiempo...",
        'invalid_file_type': "Tipo de archivo inválido. Por favor, sube un archivo tipo {expected_type}.",
        'json_error': "Error al leer el archivo JSON. Asegúrate de que sea un JSON válido.",
        'video_note_not_allowed': "Las notas de video no son compatibles. Por favor, sube un archivo de video regular.",
        # --- Tекстos para comandos de menú ---
        'command_instruction_desc': "Mostrar instrucciones del bot",
        'command_change_interface_lang_desc': "Cambiar idioma de interfaz",
        'command_change_processing_lang_desc': "Cambiar idioma de subtítulos/narración",
        'command_change_style_desc': "Cambiar estilo de procesamiento",
        'description': "❔ Lo que hace el bot:\n\n"
                       "🔊 agrega la formación profesional de los doblajes y subtítulos en 5 idiomas 🌍 (ruso, inglés, chino, español, hindi)\n"
                       "💻 conserva todos los elementos originales (jugadores, tablero de ajedrez y la música)\n"
                       "🎵 resalta los momentos clave del partido con una perfecta sincronización\n"
                       "🎥 convierte en verticales de rodillos optimizado para YouTube Shorts 📱\n\n"
                       "🎯 Resultado:\n"
                       "dinámicos, informativos y elegantes, vídeo, listos para su publicación!\n\n"
                       "🎮 Cómo funciona:\n\n"
                       "🗣️ seleccione el idioma de la interfaz\n"
                       "🎨 defina el estilo de procesamiento:\n"
                       "educativo (análisis detallado con énfasis en tácticas) o entretenido (memes, efectos y acompañamiento humorístico)\n"
                       "🔊 especifique el idioma para los Subtítulos y la actuación de voz\n"
                       "📤 descargue el video original\n\n"
    },
    'zh': {
        'welcome': "欢迎！\n\n"
                    "❔ 机器人做什么：\n\n"
                       "🔊 增加了专业的配音和5种语言（俄语，英语，中文，西班牙语，印地语）的字幕\n"
                       "💻 保留了所有原始元素（玩家，棋盘和音乐）\n"
                       "🎵 突出了党的关键时刻与完美的同步\n"
                       "🎥 将它们转换为针对YouTube短片优化的垂直视频📱\n\n"
                       "🎯 结果:\n"
                       "动态, 信息和时尚设计的视频, 准备出版!\n\n"
                       "🎮 它是如何工作的：\n\n"
                       "🗣️ 选择界面语言\n"
                       "🎨 定义处理风格：\n"
                       "教育（详细分析，重点是战术）或娱乐（模因，效果和幽默伴奏）\n"
                       "🔊 指定字幕和画外音的语言\n"
                       "📤 下载原视频\n\n"
                       "1⃣开始时，选择界面语言:",
        'start_button': "🟢 开始使用机器人",
        'select_interface_language': "请选择你偏好的界面语言：",
        'interface_language_selected': "界面语言已设置为：{language}。",
        'style_selection': "太棒了！现在选择处理风格：",
        'educational_style': "📘 教育风格（深度分析）",
        'funny_style': "🎭 娱乐风格（表情包和幽默）",
        'style_selected': "已选择教育风格。太棒了！",
        'funny_style_selected': "已选择娱乐风格。正在准备表情包！",
        'select_processing_language': "现在选择字幕和配音语言：",
        'processing_language_selected': "处理语言已设置为：{language}。",
        'upload_video_prompt': "很好！现在上传你的国际象棋对局视频文件：",
        'upload_video_button': "⬆️ 上传视频文件", # Кнопка осталась в текстах, но не будет использоваться в клавиатуре
        'video_received': "🎥 视频已接收。现在请上传包含对局数据的 JSON 文件。",
        'upload_json_prompt': "请上传包含对局数据的 JSON 文件。",
        'upload_json_button': "📄 上传 JSON 文件",
        'json_received': "📄 JSON 文件已接收。正在开始处理...",
        'follow_instructions': "请按照指示操作。发送请求的文件类型。",
        'select_action': "选择一个操作：",
        'invalid_input': "请使用按钮或命令进行交互。",
        'bot_description': "我将为你选择的语言添加配音和字幕！",
        'processing_started': "您的视频和 JSON 数据正在处理中。这可能需要一些时间...",
        'invalid_file_type': "文件类型无效。请上传 {expected_type} 文件。",
        'json_error': "读取 JSON 文件时出错。请确保它是有效的 JSON。",
        'video_note_not_allowed': "视频笔记不受支持。请上传常规视频文件。",
        # --- Тексты для команд меню ---
        'command_instruction_desc': "显示机器人说明",
        'command_change_interface_lang_desc': "更改界面语言",
        'command_change_processing_lang_desc': "更改字幕/配音语言",
        'command_change_style_desc': "更改处理风格",
        'description': "❔ 机器人做什么：\n\n"
                       "🔊 增加了专业的配音和5种语言（俄语，英语，中文，西班牙语，印地语）的字幕\n"
                       "💻 保留了所有原始元素（玩家，棋盘和音乐）\n"
                       "🎵 突出了党的关键时刻与完美的同步\n"
                       "🎥 将它们转换为针对YouTube短片优化的垂直视频📱\n\n"
                       "🎯 Result:\n"
                       "Dynamic, informative and stylishly designed videos, ready for publication!\n\n"
                       "🎮 How it works:\n\n"
                       "🗣️ Select the interface language\n"
                       "🎨 Define the processing style:\n"
                       "Educational (detailed analysis with an emphasis on tactics) or Entertaining (memes, effects and humorous accompaniment)\n"
                       "🔊 Specify the language for subtitles and voiceover\n"
                       "📤 Download the original video\n\n"
    },
    'hi': {
        'welcome': "स्वागत है!\n\n"
                    "❔ बॉट क्या करता है:\n\n"
                       "🔊 5 भाषाओं (रूसी, अंग्रेजी, चीनी, स्पेनिश, हिंदी) में पेशेवर आवाज अभिनय और उपशीर्षक जोड़ता है 🌍\n"
                       "💻 सभी मूल तत्वों (खिलाड़ियों, शतरंज बोर्ड और संगीत) को बरकरार रखता है\n"
                       "🎵 पार्टी के प्रमुख क्षणों को सही सिंक्रनाइज़ेशन के साथ हाईलाइट करता है\n"
                       "🎥 उन्हें यूट्यूब शॉर्ट्स के लिए अनुकूलित ऊर्ध्वाधर वीडियो में परिवर्तित करता है 📱\n\n"
                       "🎯 परिणाम:\n"
                       "गतिशील, सूचनात्मक और स्टाइलिश रूप से डिज़ाइन किए गए वीडियो, प्रकाशन के लिए तैयार!\n\n"
                       "🎮 यह कैसे काम करता है:\n\n"
                       "🗣️ इंटरफ़ेस भाषा का चयन करें\n"
                       "🎨 प्रसंस्करण शैली को परिभाषित करें:\n"
                       "शैक्षिक (रणनीति पर जोर देने के साथ विस्तृत विश्लेषण) या मनोरंजक (मेम, प्रभाव और विनोदी संगत)\n"
                       "🔊 उपशीर्षक और वॉयсओवर के लिए भाषा निर्दिष्ट करें\n"
                       "📤 मूल वीडियो डाउनलोड करें\n\n"
                       "1 शुरू करने के लिए, इंटरफ़ेस भाषा चुनें:",
        'start_button': "🟢 बॉट के साथ शुरुआत करें",
        'select_interface_language': "कृपया अपनी पसंदीदा इंटरफ़ेस भाषा चुनें:",
        'interface_language_selected': "इंटरफ़ेस भाषा सेट है: {language}।",
        'style_selection': "बहुत बढ़िया! अब प्रोसेसिंग शैली चुनें:",
        'educational_style': "📘 शैक्षिक शैली (गहन विश्लेषण)",
        'funny_style': "🎭 मनोरंजक शैली (मीम्स और हास्य)",
        'style_selected': "शैक्षिक शैली चुनी गई है। बहुत बढ़िया!",
        'funny_style_selected': "एक मनोरंजक शैली चुनी गई है। हम मीम्स तैयार कर रहे हैं!",
        'select_processing_language': "अब सबटाइटल और वॉयसओवर के लिए भाषा चुनें:",
        'processing_language_selected': "प्रोसेसिंग भाषा सेट है: {language}।",
        'upload_video_prompt': "उत्तम! अब अपनी शतरंज खेल की वीडियो फ़ाइल अपलोड करें:",
        'upload_video_button': "⬆️ वीडियो फ़ाइल अपलोड करें", # Кнопka осталась в текстах, но не будет использоваться в клавиатуре
        'video_received': "🎥 वीडियो प्राप्त हो गया है। अब कृपया गेम डेटा के साथ JSON फ़ाइल अपलोड करें।",
        'upload_json_prompt': "कृपया गेम डेटा के साथ JSON फ़ाइल अपलोड करें।",
        'upload_json_button': "📄 JSON फ़ाइल अपलोड करें",
        'json_received': "📄 JSON फ़ाइल प्राप्त हो गई है। प्रोसेसिंग शुरू हो रही है...",
        'follow_instructions': "कृपया निर्देशों का पालन करें। बटनों का उपयोग करें या अनुरोधित फ़ाइल प्रकार भेजें।",
        'select_action': "एक क्रिया चुनें:",
        'invalid_input': "कृपया इंटरैक्ट करने के लिए बटनों या कमांड का उपयोग करें।",
        'bot_description': "मैं आपकी चुनी हुई भाषा में वॉयс एक्टिंग и субтитлы जोड़ूंगा!",
        'processing_started': "आपके वीडियो और JSON डेटा संसाधित किए जा रहे हैं। इसमें कुछ समय लग सकता है...",
        'invalid_file_type': "अमान्य फ़ाइल प्रकार। कृपया {expected_type} फ़ाइल अपलोड करें।",
        'json_error': "JSON फ़ाइल पढ़ने में त्रुटि। कृपया सुनिश्चित करें कि यह एक मान्य JSON है।",
        'video_note_not_allowed': "वीडियो नोट्स समर्थित नहीं हैं। कृपया एक नियमित वीडियो फ़ाइल अपलोड करें।",
        # --- Тексты для команд меню ---
        'command_instruction_desc': "बॉट निर्देश दिखाएँ",
        'command_change_interface_lang_desc': "इंटरफ़ेस भाषा बदलें",
        'command_change_processing_lang_desc': "सबटाइटल/वॉयсओवर भाषा बदलें",
        'command_change_style_desc': "प्रोसेसिंग शैली बदलें",
        'description': "❔ बॉट क्या करता है:\n\n"
                       "🔊 5 भाषाओं (रूसी, अंग्रेजी, चीनी, स्पेनिश, हिंदी) में पेशेवर आवाज अभिनय और उपशीर्षक जोड़ता है 🌍\n"
                       "💻 सभी मूल तत्वों (खिलाड़ियों, शतरंज बोर्ड और संगीत) को बरकरार रखता है\n"
                       "🎵 पार्टी के प्रमुख क्षणों को सही सिंक्रनाइज़ेशन के साथ हाईलाइट करता है\n"
                       "🎥 उन्हें यूट्यूब शॉर्ट्स के लिए अनुकूलित ऊर्ध्वाधर वीडियो में परिवर्तित करता है 📱\n\n"
                       "🎯 परिणाम:\n"
                       "गतिशील, सूचनात्मक और स्टाइलिश रूप से डिज़ाइन किए गए वीडियो, प्रकाशन के लिए तैयार!\n\n"
                       "🎮 यह कैसे काम करता है:\n\n"
                       "🗣️ इंटरफ़ेस भाषा का चयन करें\n"
                       "🎨 определите стиль обработки:\n"
                       "शैक्षिक (रणनी रणनीति पर जोर देने के साथ विस्तृत विश्लेषण) или मनोरंजक (मेम, प्रभाव और विनोदित संगत)\n"
                       "🔊 укажите язык для субтитров и озвучки\n"
                       "📤 загрузите исходное видео\n\n"
    }
}

language_buttons = {
    "🇷🇺 Русский": 'ru',
    "🇺🇸 English": 'en',
    "🇪🇸 Español": 'es',
    "🇮🇳 हिन्दी": 'hi',
    "🇨🇳 中文": 'zh'
}

# --- Определение команд для меню ---
def get_commands_for_language(lang):
    """Возвращает список команд для меню на заданном языке."""
    commands = [
        telebot.types.BotCommand("/description", texts[lang]['command_instruction_desc']),
        telebot.types.BotCommand("/change_interface_lang", texts[lang]['command_change_interface_lang_desc']),
        telebot.types.BotCommand("/change_processing_lang", texts[lang]['command_change_processing_lang_desc']),
        telebot.types.BotCommand("/change_style", texts[lang]['command_change_style_desc']),
    ]
    return commands

# --- Функции создания клавиатур ---
def create_interface_language_selection_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [types.KeyboardButton(text) for text in language_buttons]
    markup.row(buttons[0], buttons[1])
    markup.row(buttons[2], buttons[3], buttons[4])
    return markup

def create_processing_language_selection_inline_keyboard():
    markup = types.InlineKeyboardMarkup()
    for text, lang_code in language_buttons.items():
        markup.add(types.InlineKeyboardButton(text, callback_data=f'set_processing_lang_{lang_code}'))
    return markup

def create_style_selection_keyboard(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(texts[lang]['educational_style'])
    btn2 = types.KeyboardButton(texts[lang]['funny_style'])
    markup.add(btn1, btn2)
    return markup

# Убираем функцию create_upload_video_keyboard, так как она больше не нужна

def create_upload_json_keyboard(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton(texts[lang]['upload_json_button'])
    markup.add(btn)
    return markup

# --- Функции отправки сообщений ---
def send_welcome(chat_id):
    # Сбрасываем все данные и состояние пользователя при /start
    user_interface_languages.pop(chat_id, None)
    user_styles.pop(chat_id, None)
    user_processing_languages.pop(chat_id, None)
    user_state.pop(chat_id, None)
    user_previous_state.pop(chat_id, None) # Сбрасываем предыдущее состояние

    # Устанавливаем начальное состояние
    user_state[chat_id] = STATE_AWAITING_INTERFACE_LANG
    bot.send_message(chat_id, texts['en']['welcome'],
                    reply_markup=create_interface_language_selection_keyboard())
    bot.set_my_commands([], scope=types.BotCommandScopeChat(chat_id)) # Сбрасываем команды меню при старте


def send_style_selection(chat_id):
    lang = user_interface_languages.get(chat_id, 'en')
    user_state[chat_id] = STATE_AWAITING_STYLE
    markup = create_style_selection_keyboard(lang)
    bot.send_message(chat_id, texts[lang]['style_selection'], reply_markup=markup)


def send_interface_language_selection(chat_id):
    lang = user_interface_languages.get(chat_id, 'en')
    user_state[chat_id] = STATE_AWAITING_INTERFACE_LANG
    bot.send_message(chat_id, texts[lang]['select_interface_language'], reply_markup=create_interface_language_selection_keyboard())

def send_processing_language_selection(chat_id):
    lang = user_interface_languages.get(chat_id, 'en')
    user_state[chat_id] = STATE_AWAITING_PROCESSING_LANG
    markup = create_processing_language_selection_inline_keyboard()
    bot.send_message(chat_id, texts[lang]['select_processing_language'], reply_markup=markup)

def send_upload_video_prompt(chat_id):
    lang = user_interface_languages.get(chat_id, 'en')
    user_state[chat_id] = STATE_AWAITING_VIDEO
    # Отправляем сообщение без Reply-клавиатуры
    bot.send_message(chat_id, texts[lang]['upload_video_prompt'], reply_markup=types.ReplyKeyboardRemove())


def send_upload_json_prompt(chat_id):
    lang = user_interface_languages.get(chat_id, 'en')
    user_state[chat_id] = STATE_AWAITING_JSON
    # Отправляем сообщение с Reply-клавиатурой для кнопки "Загрузить JSON файл"
    #markup = create_upload_json_keyboard(lang) # Убираем клавиатуру, ожидаем просто файл
    bot.send_message(chat_id, texts[lang]['upload_json_prompt'], reply_markup=types.ReplyKeyboardRemove())

# Добавляем функцию для возврата к предыдущему шагу
def return_to_previous_state(chat_id):
    previous_state = user_previous_state.pop(chat_id, STATE_AWAITING_STYLE) # По умолчанию возвращаемся к стилю, если предыдущего состояния нет
    lang = user_interface_languages.get(chat_id, 'en')

    if previous_state == STATE_AWAITING_STYLE:
        send_style_selection(chat_id)
    elif previous_state == STATE_AWAITING_PROCESSING_LANG:
        send_processing_language_selection(chat_id)
    elif previous_state == STATE_AWAITING_VIDEO:
        send_upload_video_prompt(chat_id)
    elif previous_state == STATE_AWAITING_JSON:
        send_upload_json_prompt(chat_id)
    # Добавьте другие состояния, если необходимо

# --- Установка меню команд ---
def set_user_commands(chat_id, lang_code):
    """Устанавливает меню команд для конкретного пользователя."""
    commands = get_commands_for_language(lang_code)
    bot.set_my_commands(commands, scope=types.BotCommandScopeChat(chat_id))

# --- Обработчики команд меню ---
@bot.message_handler(commands=['description'])
def handle_instruction_command(message):
    chat_id = message.chat.id
    lang = user_interface_languages.get(chat_id, 'en')
    bot.send_message(chat_id, texts[lang]['description'], reply_markup=types.ReplyKeyboardRemove()) # Убираем клавиатуру, т.к. это информационная команда

@bot.message_handler(commands=['change_interface_lang'])
def handle_change_interface_lang_command(message):
    chat_id = message.chat.id
    # Сохраняем текущее состояние перед изменением языка интерфейса
    current_state = user_state.get(chat_id)
    if current_state and current_state != STATE_AWAITING_INTERFACE_LANG:
        user_previous_state[chat_id] = current_state

    # Предлагаем выбрать язык интерфейса заново
    send_interface_language_selection(chat_id)


@bot.message_handler(commands=['change_processing_lang'])
def handle_change_processing_lang_command(message):
    chat_id = message.chat.id
    lang = user_interface_languages.get(chat_id, 'en')

    # Проверяем, выбран ли уже стиль. Если нет, просим выбрать стиль сначала.
    if chat_id not in user_styles:
         bot.send_message(chat_id, texts[lang]['invalid_input']) # Или более специфичное сообщение
         send_style_selection(chat_id) # Предлагаем выбрать стиль
         return

    # Сбрасываем язык обработки, предлагаем выбрать язык обработки заново с Inline кнопками
    user_processing_languages.pop(chat_id, None)
    send_processing_language_selection(chat_id)


@bot.message_handler(commands=['change_style'])
def handle_change_style_command(message):
    chat_id = message.chat.id
    lang = user_interface_languages.get(chat_id, 'en')

    # Сбрасываем стиль и язык обработки, предлагаем выбрать стиль заново
    user_styles.pop(chat_id, None)
    user_processing_languages.pop(chat_id, None)
    send_style_selection(chat_id)


# --- Обработчик команды /start ---
@bot.message_handler(commands=['start'])
def handle_start(message):
    send_welcome(message.chat.id)


# --- Обработчик текстовых сообщений ---
# Этот хэндлер теперь обрабатывает ТОЛЬКО текстовые сообщения
@bot.message_handler(func=lambda m: m.content_type == 'text')
def handle_text_messages(message):
    chat_id = message.chat.id
    user_input = message.text
    current_state = user_state.get(chat_id)
    interface_lang_code = user_interface_languages.get(chat_id, 'en') # Берем язык интерфейса, если установлен

    # Обработка в зависимости от текущего состояния пользователя
    if current_state == STATE_AWAITING_INTERFACE_LANG:
        # Обработка выбора языка интерфейса
        if user_input in language_buttons:
            selected_lang_code = language_buttons[user_input]
            user_interface_languages[chat_id] = selected_lang_code
            set_user_commands(chat_id, selected_lang_code)
            bot.send_message(chat_id, texts[selected_lang_code]['interface_language_selected'].format(language=user_input), reply_markup=types.ReplyKeyboardRemove())

            # Возвращаемся к предыдущему шагу или переходим к выбору стиля
            if chat_id in user_previous_state:
                return_to_previous_state(chat_id)
            else:
                send_style_selection(chat_id) # Переходим к выбору стиля, если язык выбран впервые
        else:
            bot.send_message(chat_id, texts[interface_lang_code]['invalid_input']) # Используем язык по умолчанию или уже выбранный
            send_interface_language_selection(chat_id) # Просим выбрать снова

    elif current_state == STATE_AWAITING_STYLE:
        # Обработка выбора стиля
        educational_text = texts[interface_lang_code]['educational_style']
        funny_text = texts[interface_lang_code]['funny_style']

        if user_input == educational_text:
            user_styles[chat_id] = "educational"
            bot.send_message(chat_id, educational_text, reply_markup=types.ReplyKeyboardRemove())
            send_processing_language_selection(chat_id) # Переходим к выбору языка обработки
        elif user_input == funny_text:
            user_styles[chat_id] = "funny"
            bot.send_message(chat_id, funny_text, reply_markup=types.ReplyKeyboardRemove())
            send_processing_language_selection(chat_id) # Переходим к выбору языка обработки
        else:
            bot.send_message(chat_id, texts[interface_lang_code]['invalid_input'])
            send_style_selection(chat_id) # Просим выбрать снова

    elif current_state == STATE_AWAITING_VIDEO:
        # Если получили текст в состоянии ожидания видео
        bot.send_message(chat_id, texts[interface_lang_code]['invalid_file_type'].format(expected_type='video'))
        send_upload_video_prompt(chat_id) # Просим загрузить видео снова

    #elif current_state and current_state['state'] == STATE_AWAITING_JSON: # Убрана проверка на словарь, user_state теперь просто строка
    elif current_state == STATE_AWAITING_JSON:
        # Если получили текст в состоянии ожидания JSON
        bot.send_message(chat_id, texts[interface_lang_code]['invalid_file_type'].format(expected_type='JSON'))
        send_upload_json_prompt(chat_id) # Просим загрузить JSON снова

    else:
        # Неожиданный текстовый ввод в других состояниях
        bot.send_message(chat_id, texts[interface_lang_code]['invalid_input'])


@bot.callback_query_handler(func=lambda call: call.data.startswith('set_processing_lang_'))
def handle_processing_language_callback(call):
    chat_id = call.message.chat.id
    selected_lang_code = call.data.replace('set_processing_lang_', '')
    interface_lang_code = user_interface_languages.get(chat_id, 'en')

    if selected_lang_code in texts:
        user_processing_languages[chat_id] = selected_lang_code
        selected_lang_name = ""
        for name, code in language_buttons.items():
            if code == selected_lang_code:
                selected_lang_name = name
                break

        try:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=texts[interface_lang_code]['processing_language_selected'].format(language=selected_lang_name))
        except Exception as e:
             print(f"Error editing message: {e}")
             bot.send_message(chat_id, texts[interface_lang_code]['processing_language_selected'].format(language=selected_lang_name), reply_markup=types.ReplyKeyboardRemove())

        send_upload_video_prompt(chat_id) # Переходим к загрузке видео
    else:
        bot.send_message(chat_id, texts[interface_lang_code]['invalid_input'])

    bot.answer_callback_query(call.id)

# ... (предыдущий код остается без изменений до функции handle_files)

@bot.message_handler(content_types=['video', 'document'])
def handle_files(message):
    chat_id = message.chat.id
    current_state = user_state.get(chat_id)
    lang = user_interface_languages.get(chat_id, 'en')

    # Проверяем, находится ли пользователь на этапе ожидания видео
    if current_state == STATE_AWAITING_VIDEO:
        # Если получен ВИДЕО файл
        if message.content_type == 'video':
            # Проверяем, что это не видео-кружок (video_note)
            if message.video_note:
                bot.send_message(chat_id, texts[lang]['video_note_not_allowed'])
                send_upload_video_prompt(chat_id)
                return

            bot.send_message(chat_id, texts[lang]['video_received'], reply_markup=types.ReplyKeyboardRemove())

            try:
                # Сохраняем видео файл
                file_info = bot.get_file(message.video.file_id)
                downloaded_file = bot.download_file(file_info.file_path)

                file_extension = os.path.splitext(file_info.file_path)[1]
                video_filename = f"{chat_id}_{message.video.file_id}{file_extension}"
                video_filepath = os.path.join(VIDEO_DIR, video_filename)

                with open(video_filepath, 'wb') as new_file:
                    new_file.write(downloaded_file)

                # Переходим в состояние ожидания JSON, сохраняя путь к видео
                user_state[chat_id] = {'state': STATE_AWAITING_JSON, 'video_path': video_filepath}
                send_upload_json_prompt(chat_id)

            except Exception as e:
                print(f"Error downloading video: {e}")
                bot.send_message(chat_id, "Ошибка при загрузке видео. Попробуйте еще раз.")
                send_upload_video_prompt(chat_id)

        # Если получен документ вместо видео
        else:
            bot.send_message(chat_id, texts[lang]['invalid_file_type'].format(expected_type='video'))
            send_upload_video_prompt(chat_id)

    # Ожидаем JSON файл
    #elif current_state and current_state['state'] == STATE_AWAITING_JSON: # Убрана проверка на словарь, user_state теперь может быть строкой
    elif current_state == STATE_AWAITING_JSON: # Проверяем, что это словарь и в нем есть ключ state со значением STATE_AWAITING_JSON
        if message.content_type == 'document':
            file_name = message.document.file_name

            # Строгая проверка на JSON файл
            if not file_name or not file_name.lower().endswith('.json'):
                bot.send_message(chat_id, texts[lang]['invalid_file_type'].format(expected_type='JSON'))
                send_upload_json_prompt(chat_id)
                return

            try:
                # Скачиваем и проверяем JSON
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                '''
                # Проверяем валидность JSON
                try:
                    json_data = json.loads(downloaded_file.decode('utf-8'))
                except json.JSONDecodeError:
                    bot.send_message(chat_id, texts[lang]['json_error'])
                    send_upload_json_prompt(chat_id)
                    return
                '''
                # Сохраняем JSON
                json_filename = f"{chat_id}_{message.document.file_id}.json"
                json_filepath = os.path.join(JSON_DIR, json_filename)
                
                # Создаем директорию, если ее нет
                os.makedirs(JSON_DIR, exist_ok=True)
                
                with open(json_filepath, 'wb') as new_file:
                    new_file.write(downloaded_file)


            except Exception as e:
                print(f"Error processing JSON: {e}")
                bot.send_message(chat_id, "Ошибка при обработке файла. Попробуйте еще раз.")
                send_upload_json_prompt(chat_id)

        # Если получено не документ
        else:
            bot.send_message(chat_id, texts[lang]['invalid_file_type'].format(expected_type='JSON'))
            send_upload_json_prompt(chat_id)

# Новый обработчик для текстовых сообщений при ожидании файлов
@bot.message_handler(func=lambda m: m.content_type == 'text' and 
                                  user_state.get(m.chat.id) in [STATE_AWAITING_VIDEO, STATE_AWAITING_JSON])
def handle_text_during_file_await(message):
    chat_id = message.chat.id
    lang = user_interface_languages.get(chat_id, 'en')
    current_state = user_state.get(chat_id)
    
    if current_state == STATE_AWAITING_VIDEO:
        bot.send_message(chat_id, texts[lang]['invalid_file_type'].format(expected_type='video'))
        send_upload_video_prompt(chat_id)
    elif current_state == STATE_AWAITING_JSON:
        bot.send_message(chat_id, texts[lang]['invalid_file_type'].format(expected_type='JSON'))
        send_upload_json_prompt(chat_id)


# --- Обработчик всех остальных типов сообщений ---
# Этот хэндлер будет ловить сообщения, которые не являются текстом, видео или документом
@bot.message_handler(func=lambda m: True, content_types=['audio', 'photo', 'sticker', 'voice', 'contact', 'location', 'venue', 'game', 'invoice', 'successful_payment', 'video_note', 'poll', 'quiz', 'animation'])
def handle_unwanted_messages(message):
    chat_id = message.chat.id
    lang = user_interface_languages.get(chat_id, 'en')
    current_state = user_state.get(chat_id)

    # Отправляем сообщение об ошибке в зависимости от состояния пользователя
    if current_state == STATE_AWAITING_VIDEO:
         bot.send_message(chat_id, texts[lang]['invalid_file_type'].format(expected_type='video'))
         send_upload_video_prompt(chat_id) # Просим загрузить видео снова
    elif current_state == STATE_AWAITING_JSON:
    #elif current_state and current_state['state'] == STATE_AWAITING_JSON:
         # Этот случай уже обрабатывается в handle_files, но на всякий случай оставим
         bot.send_message(chat_id, texts[lang]['invalid_file_type'].format(expected_type='JSON'))
         send_upload_json_prompt(chat_id) # Показываем клавиатуру JSON снова
    else:
        # В других состояниях, просто сообщаем о неверном вводе
        bot.send_message(chat_id, texts[lang]['invalid_input'])


# --- Запуск бота ---
print("Bot started...")
bot.infinity_polling()