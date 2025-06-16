import time
import random
from typing import TypeVar, Callable, Any
from google.api_core.exceptions import ResourceExhausted

T = TypeVar('T')

def retry_with_backoff(
    func: Callable[..., T],
    max_retries: int = 5,
    base_delay: float = 2.0,
    *args: Any,
    **kwargs: Any
) -> T:
    """
    Retry a function with exponential backoff when hitting rate limits.
    
    Args:
        func: The function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for the first retry
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
    
    Returns:
        The result of the function if successful
        
    Raises:
        ResourceExhausted: If all retries are exhausted
        Exception: Any other exception from the function
    """
    retry_count = 0
    while True:
        try:
            return func(*args, **kwargs)
        except ResourceExhausted as e:
            retry_count += 1
            if retry_count >= max_retries:
                print(f"Max retries ({max_retries}) exceeded.")
                raise
            
            delay = base_delay * (2 ** (retry_count - 1))
            jitter = random.uniform(0, 0.1 * delay)
            total_delay = delay + jitter
            
            print(f"Rate limit hit. Retrying in {total_delay:.2f} seconds (attempt {retry_count}/{max_retries})")
            time.sleep(total_delay)