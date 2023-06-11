import asyncio


async def run_sync(func: callable, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        func,
        *args,
        **kwargs,
    )
