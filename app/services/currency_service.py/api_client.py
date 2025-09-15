import aiohttp
import asyncio
import json
from app.core.logger_config import get_logger
from datetime import datetime


logger = get_logger(__name__)


class CurrencyParser:

    # Получение курса валют через API

    def __init__(self, url: str = "https://www.cbr-xml-daily.ru/daily_json.js"):
        self.url = url

    async def get_currency_rates(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url, timeout=10) as response:
                    if response.status == 200:

                        data = await response.json(content_type=None)
                        return data
                    else:
                        raise Exception(
                            f"Ошибка получения данных: status code : {response.status}"
                        )

        except Exception as e:
            logger.error(f"Произошла ошибка получения данных: {e}")

    async def extract_currency_data(self):
        data = await self.get_currency_rates()
        if data:

            try:
                valutes = data["Valute"]

                currency_data = {
                    "Timestamp": data.get("Timestamp"),
                    "Date": data.get("Date", ""),
                    "rates": {
                        "USD": {
                            "value": valutes["USD"]["Value"],
                            "char_code": valutes["USD"]["CharCode"],
                        },
                        "EUR": {
                            "value": valutes["EUR"]["Value"],
                            "char_code": valutes["EUR"]["CharCode"],
                        },
                        "GBP": {
                            "value": valutes["GBP"]["Value"],
                            "char_code": valutes["GBP"]["CharCode"],
                        },
                    },
                }

                logger.info("Данные успешно получены!")
                return currency_data
            except Exception as e:
                logger.error(f"Произошла ошибка получения данных: {e}")

        return None


if __name__ == "__main__":
    asyncio.run()
