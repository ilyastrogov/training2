""" Параметры метода — когда:

взаимодействие временное;

нужно передать разные реализации в зависимости от ситуации.

Частые ошибки
Избыточное наследование — не создавайте иерархии там, где достаточно композиции.

Нарушение инкапсуляции — не обращайтесь к приватным атрибутам (_private) другого класса.

Циклические зависимости — избегайте взаимного импорта классов.

Жёсткая связь — используйте интерфейсы или абстракции для агрегации, чтобы снизить зависимость.

Хотите, я раскрою какой‑то подход подробнее или помогу адаптировать код под ваш конкретный случай?"""
class Logger:
    def log(self, message):
        print(f"[LOG] {message}")

class Processor:
    def process_data(self, data, logger):  # logger — параметр метода
        logger.log("Начало обработки")
        result = data.upper()
        logger.log("Обработка завершена")
        return result

# Использование
logger = Logger()
processor = Processor()
result = processor.process_data("hello", logger)
print(result)

""" Решение: использование абстракций
Абстракция — это выделение общего интерфейса без привязки к конкретной реализации. В ООП это реализуется через:

интерфейсы (в языках с их поддержкой);

абстрактные классы;

протоколы (в Python).

Шаг 1. Создаём абстракцию (интерфейс)
Определим контракт для всех хранилищ данных: """

from abc import ABC, abstractmethod

class DataStorage(ABC):
    @abstractmethod
    def save(self, data):
        pass

    @abstractmethod
    def load(self, key):
        pass

""" Шаг 2. Реализуем разные версии через абстракцию
Создадим несколько реализаций, соответствующих интерфейсу: """
class DatabaseStorage(DataStorage):
    def save(self, data):
        print(f"Saving {data} to PostgreSQL")

    def load(self, key):
        return f"Data {key} from PostgreSQL"

class FileStorage(DataStorage):
    def save(self, data):
        print(f"Saving {data} to file system")

    def load(self, key):
        return f"Data {key} from file"

class CacheStorage(DataStorage):
    def save(self, data):
        print(f"Caching {data}")

    def load(self, key):
        return f"Cached data {key}"

""" Шаг 3. Переписываем сервис с использованием абстракции
Теперь UserService зависит не от конкретной реализации, а от абстракции: """

class UserService:
    def __init__(self, storage: DataStorage):  # Зависимость от абстракции
        self.storage = storage

    def create_user(self, user_data):
        self.storage.save(user_data)

    def get_user(self, user_id):
        return self.storage.load(user_id)

""" Шаг 4. Используем разные реализации
Теперь можно легко подменять хранилища: """


# Используем базу данных
db_storage = DatabaseStorage()
user_service_db = UserService(db_storage)
user_service_db.create_user({"name": "Alice"})
user_service_db.create_user({"name": "Vova"})

# Используем файловое хранилище
file_storage = FileStorage()
user_service_file = UserService(file_storage)
user_service_file.create_user({"name": "Bob"})

# Используем кэш
cache_storage = CacheStorage()
user_service_cache = UserService(cache_storage)
user_service_cache.create_user({"name": "Charlie"})