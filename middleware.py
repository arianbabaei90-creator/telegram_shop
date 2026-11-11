from aiogram import BaseMiddleware

class mymidleware(BaseMiddleware):
    async def __call__(self, handler,event,data):
        print("message resived")
        return await handler(event,data)