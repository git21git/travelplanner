"""
Главный файл запуска приложения TravelPlanner.
"""
import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Получение порта и хоста из переменных окружения
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'

    app.run(host=host, port=port, debug=debug)
