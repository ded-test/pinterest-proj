from fastapi.templating import Jinja2Templates
import os
from pathlib import Path

# Получаем абсолютный путь к корню проекта (где находятся app, frontend, tests)
BASE_DIR = Path(__file__).resolve().parent.parent  # Поднимаемся из app в корень

# Правильный путь к templates
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"

# Создаем объект templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Для отладки можно добавить проверку
print(f"Templates directory: {TEMPLATES_DIR}")
print(f"Directory exists: {TEMPLATES_DIR.exists()}")
print(f"chat.html exists: {(TEMPLATES_DIR / 'chat.html').exists()}")
