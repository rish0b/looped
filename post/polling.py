import asyncio
import time
from .utils import setup_logger
from concurrent.futures import ThreadPoolExecutor

# Initialize ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=5)

async def start_polling(self, handler, message_id, callback, interval=5, duration=60, silent=False):
    # Set up logger based on the silent parameter
    self.logger = setup_logger(silent)

    start_time = time.time()

    if not silent:
        self.logger.info(f"Started polling for message ID: {message_id}.")

    loop = asyncio.get_event_loop()

    while time.time() - start_time < duration:
        # Run check_for_feedback in a separate thread
        feedback = await loop.run_in_executor(executor, handler.check_for_feedback, message_id)
        
        if feedback:
            if not silent:
                self.logger.info(f"Feedback received for message ID: {message_id}.")
            callback(feedback)
            return feedback
        
        if not silent:
            self.logger.info(f"No feedback yet for message ID: {message_id}, retrying in {interval} seconds.")
        
        await asyncio.sleep(interval)

    if not silent:
        self.logger.info(f"Polling timed out for message ID: {message_id}. No feedback received within {duration} seconds.")
    
    return None