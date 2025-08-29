import aiohttp
from config import settings
import asyncio
import json


async def get_usd():
    async with aiohttp.ClientSession() as session:
        async with session.get(settings.URL) as response:
            text_data = await response.text()
            data = json.loads(text_data)
            usd = data["Valute"]["USD"]["Value"]
            return usd


result = asyncio.run(get_usd())
print(result)
