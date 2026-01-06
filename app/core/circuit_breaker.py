"""
Circuit Breaker Pattern
"""
from enum import Enum
from typing import Callable, TypeVar
from datetime import datetime, timedelta
import redis
from app.core.config import settings
from loguru import logger

T = TypeVar('T')

try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    logger.warning(f"Redis connection failed for circuit breaker: {e}")
    redis_client = None


class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker implementation"""
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.key_prefix = f"circuit_breaker:{name}"
    
    def _get_state(self) -> CircuitState:
        """Get current circuit breaker state"""
        if redis_client is None:
            return CircuitState.CLOSED
        
        state = redis_client.get(f"{self.key_prefix}:state")
        if state is None:
            return CircuitState.CLOSED
        return CircuitState(state)
    
    def _set_state(self, state: CircuitState):
        """Set circuit breaker state"""
        if redis_client is None:
            return
        
        redis_client.set(f"{self.key_prefix}:state", state.value)
        if state == CircuitState.OPEN:
            # Set timeout
            redis_client.expire(f"{self.key_prefix}:state", self.timeout)
    
    def _increment_failures(self) -> int:
        """Increment failure count"""
        if redis_client is None:
            return 0
        
        count = redis_client.incr(f"{self.key_prefix}:failures")
        redis_client.expire(f"{self.key_prefix}:failures", self.timeout)
        return count
    
    def _reset_failures(self):
        """Reset failure count"""
        if redis_client is None:
            return
        redis_client.delete(f"{self.key_prefix}:failures")
    
    def call(self, func: Callable, *args, **kwargs) -> T:
        """Call function with circuit breaker protection"""
        state = self._get_state()
        
        if state == CircuitState.OPEN:
            # Check if timeout expired
            if redis_client:
                ttl = redis_client.ttl(f"{self.key_prefix}:state")
                if ttl > 0:
                    raise Exception(f"Circuit breaker is OPEN. Try again in {ttl} seconds.")
                else:
                    # Timeout expired, try half-open
                    self._set_state(CircuitState.HALF_OPEN)
                    state = CircuitState.HALF_OPEN
        
        # Try to call function
        try:
            result = func(*args, **kwargs)
            
            # Success - reset failures and close circuit
            if state == CircuitState.HALF_OPEN:
                self._set_state(CircuitState.CLOSED)
            self._reset_failures()
            
            return result
            
        except self.expected_exception as e:
            # Failure - increment counter
            failures = self._increment_failures()
            
            if failures >= self.failure_threshold:
                # Open circuit
                self._set_state(CircuitState.OPEN)
                logger.error(f"Circuit breaker {self.name} opened after {failures} failures")
            
            raise

