import time
import logging
import functools
from typing import Callable, Any

logger = logging.getLogger(__name__)

def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0, exponential: bool = True):
    """
    Decorator for retrying functions with exponential backoff.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Final retry attempt failed for {func.__name__}: {e}")
                        raise e
                    
                    delay = base_delay * (2 ** (retries - 1)) if exponential else base_delay
                    logger.warning(f"Error in {func.__name__}: {e}. Retrying in {delay}s... ({retries}/{max_retries})")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator
