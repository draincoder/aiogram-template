import asyncpg


class Database:

    def __init__(self, conn):
        self.conn: asyncpg.connection = conn

    async def get_users(self) -> None:
        return await self.conn.fetch('SELECT * FROM users')
