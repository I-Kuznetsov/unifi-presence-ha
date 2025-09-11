import aiohttp
import async_timeout
import time

class UniFiApi:
    def __init__(self, host, username, password, site="default", verify_ssl=False):
        self.host = host
        self.username = username
        self.password = password
        self.site = site
        self.verify_ssl = verify_ssl
        self._session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar())

    async def login(self):
        url = f"{self.host}/api/login"
        payload = {"username": self.username, "password": self.password}
        async with async_timeout.timeout(10):
            async with self._session.post(url, json=payload, ssl=self.verify_ssl) as resp:
                if resp.status != 200:
                    raise Exception(f"Login failed {resp.status}")

    async def get_clients(self):
        await self.login()
        url = f"{self.host}/api/s/{self.site}/stat/sta"
        async with async_timeout.timeout(10):
            async with self._session.get(url, ssl=self.verify_ssl) as resp:
                data = await resp.json()
                clients = []
                now = int(time.time())
                for c in data.get("data", []):
                    identity = c.get("1x_identity") or c.get("hostname") or c.get("mac")
                    if not identity:
                        continue
                    last_seen = c.get("last_seen", now)
                    is_active = (now - last_seen) < 60
                    c["is_active"] = is_active
                    clients.append(c)
                return clients
