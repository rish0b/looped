import time
import asyncio

class Polling:
    def __init__(self, silent=False):
        self.silent = silent    # NEED TO ADD LOGGING AND THIS WILL SILENCE LOGS
    
    async def start_polling(self, handler, message_id, callback, interval=5, duration=60):
        start_time = time.time()
        while time.time() - start_time < duration:
            feedback = await handler.check_for_feedback(message_id)
            if feedback:
                callback(feedback)
                return feedback
            await asyncio.sleep(interval)
        return None