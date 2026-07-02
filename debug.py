import asyncio
import aiohttp
from crawler import get_all_website_links, get_base_domain

async def main():
    async with aiohttp.ClientSession() as session:
        url = "https://google.com"
        domain = get_base_domain(url)
        print("Base domain:", domain)
        urls = await get_all_website_links(session, url, domain)
        print("Discovered:", len(urls))
        for k in urls:
            print(k)

asyncio.run(main())
