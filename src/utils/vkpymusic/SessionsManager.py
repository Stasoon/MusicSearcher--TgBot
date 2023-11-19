import random

import asyncio
from cachetools import TTLCache

from .Session import Session


class SessionsManager:
    __instance = None
    services: dict[str, Session] = {}
    service_cache = TTLCache(maxsize=50, ttl=1.5)

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __del__(self):
        SessionsManager.__instance = None

    def add_session(self, session: Session):
        n = 0
        while session.name in self.services:
            session.name += f'_{n}'; n += 1
        self.services[session.name] = session

    async def get_available_service(self) -> Session:
        while True:
            # Неиспользованные сервисы
            not_used = [service_name for service_name in self.services if service_name not in self.service_cache]
            # Сервисы, в которых нет превышения лимита
            not_exceeded = [ser for ser in self.service_cache.keys() if self.service_cache.get(ser) < 3]
            available_services = not_used + not_exceeded

            # Если нет доступных сервисов, ждём пол секунды и пробуем снова
            if not available_services:
                await asyncio.sleep(1)
                continue
            # Если есть неиспользованные сервисы, берём первый из них
            if not_used:
                service_name = random.choice(not_used)
                self.service_cache[service_name] = 0
            # Иначе берём наименее загруженный
            else:
                service_name = min(not_exceeded, key=self.service_cache.get)

            service = self.services[service_name]
            self.service_cache[service_name] += 1
            return service
