# © 2025 The Christman AI Project. All rights reserved.
#
# This code is released as part of a trauma-informed, dignity-first AI ecosystem
# designed to protect, empower, and elevate vulnerable populations.
#
# By using, modifying, or distributing this software, you agree to uphold the following:
# 1. Truth — No deception, no manipulation.
# 2. Dignity — Respect the autonomy and humanity of all users.
# 3. Protection — Never use this to exploit or harm vulnerable individuals.
# 4. Transparency — Disclose all modifications and contributions clearly.
# 5. No Erasure — Preserve the mission and ethical origin of this work.
#
# This is not just code. This is redemption in code.
# Contact: lumacognify@thechristmanaiproject.com
# https://thechristmanaiproject.com
import logging
import time
import functools
from enum import Enum
from typing import Callable, Any, Dict, List, Optional, Union, TypeVar, cast

# Type definition for the decorated function
F = TypeVar('F', bound=Callable[..., Any])

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = 'closed'      # Normal operation, requests pass through
    OPEN = 'open'          # Circuit is open, requests fail fast
    HALF_OPEN = 'half_open'  # Testing if the circuit can be closed again


class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open"""
    pass


class CircuitBreaker:
    """
    Circuit breaker pattern implementation to handle service failures gracefully.
    When a service fails repeatedly, the circuit opens and fails fast to prevent
    cascading failures and allow the service time to recover.
    """
    
    # Class-level tracking of circuit breakers by name
    _circuit_breakers: Dict[str, 'CircuitBreaker'] = {}
    
    @classmethod
    def get_circuit_breaker(cls, name: str) -> Optional['CircuitBreaker']:
        """Get a circuit breaker by name"""
        return cls._circuit_breakers.get(name)
    
    @classmethod
    def get_all_circuit_breakers(cls) -> Dict[str, 'CircuitBreaker']:
        """Get all circuit breakers"""
        return cls._circuit_breakers.copy()
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        timeout_threshold: int = 10,
        fallback_function: Optional[Callable[..., Any]] = None,
        exclude_exceptions: Optional[List[type]] = None
    ):
        """
        Initialize a circuit breaker
        
        Args:
            name: Unique name for this circuit breaker
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before trying to recover (half-open)
            timeout_threshold: Seconds to wait before considering a request timed out
            fallback_function: Function to call when circuit is open
            exclude_exceptions: List of exception types that shouldn't count as failures
        """
        self.logger = logging.getLogger(__name__)
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.timeout_threshold = timeout_threshold
        self.fallback_function = fallback_function
        self.exclude_exceptions = exclude_exceptions or []
        
        # State variables
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.last_success_time = time.time()
        
        # Register this circuit breaker
        CircuitBreaker._circuit_breakers[name] = self
        
        self.logger.info(f"Circuit breaker '{name}' initialized with failure threshold {failure_threshold}")
    
    def __call__(self, func: F) -> F:
        """
        Decorator to wrap a function with circuit breaker pattern
        
        Args:
            func: Function to wrap
            
        Returns:
            Wrapped function
        """
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return self.call(func, *args, **kwargs)
        
        return cast(F, wrapper)
    
    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """
        Call a function with circuit breaker pattern
        
        Args:
            func: Function to call
            args: Positional arguments for function
            kwargs: Keyword arguments for function
            
        Returns:
            The result of the function call or fallback
            
        Raises:
            CircuitBreakerError: If circuit is open and no fallback is available
        """
        self._check_state_transition()
        
        if self.state == CircuitState.OPEN:
            return self._handle_open_circuit(func, *args, **kwargs)
        
        if self.state == CircuitState.HALF_OPEN:
            return self._handle_half_open_circuit(func, *args, **kwargs)
        
        # Normal closed circuit operation
        return self._call_function(func, *args, **kwargs)
    
    def _check_state_transition(self) -> None:
        """Check and update circuit state based on time elapsed"""
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has elapsed
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.logger.info(f"Circuit breaker '{self.name}' state: OPEN -> HALF_OPEN")
    
    def _handle_open_circuit(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Handle request when circuit is open"""
        if self.fallback_function:
            self.logger.debug(f"Circuit '{self.name}' open, using fallback function")
            return self.fallback_function(*args, **kwargs)
        else:
            self.logger.debug(f"Circuit '{self.name}' open, failing fast")
            raise CircuitBreakerError(f"Circuit '{self.name}' is open")
    
    def _handle_half_open_circuit(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Handle request when circuit is half-open"""
        self.logger.debug(f"Circuit '{self.name}' half-open, testing with request")
        
        try:
            result = self._call_function(func, *args, **kwargs)
            # Success, close the circuit
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.last_success_time = time.time()
            self.logger.info(f"Circuit breaker '{self.name}' state: HALF_OPEN -> CLOSED")
            return result
        except Exception as e:
            # Failure, back to open state
            self.state = CircuitState.OPEN
            self.last_failure_time = time.time()
            self.logger.info(f"Circuit breaker '{self.name}' state: HALF_OPEN -> OPEN (test request failed)")
            
            if self.fallback_function:
                return self.fallback_function(*args, **kwargs)
            else:
                raise
    
    def _call_function(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Call function and handle failures"""
        start_time = time.time()
        
        try:
            # Set a timeout for the function call if it takes too long
            result = func(*args, **kwargs)
            
            # Check for timeout
            execution_time = time.time() - start_time
            if execution_time > self.timeout_threshold:
                self.logger.warning(
                    f"Function '{func.__name__}' took {execution_time:.2f}s, "
                    f"exceeding threshold of {self.timeout_threshold}s"
                )
                self._record_failure()
            else:
                # Success - reset failure count if needed
                if self.failure_count > 0:
                    self.failure_count = 0
                    self.logger.debug(f"Circuit '{self.name}' success, reset failure count")
                self.last_success_time = time.time()
            
            return result
            
        except Exception as e:
            # Check if this exception type should be counted as a failure
            if not any(isinstance(e, exc_type) for exc_type in self.exclude_exceptions):
                self._record_failure()
                self.logger.warning(f"Circuit '{self.name}' recorded failure: {str(e)}")
            
            raise
    
    def _record_failure(self) -> None:
        """Record a failure and check if circuit should open"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.CLOSED and self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.logger.warning(
                f"Circuit breaker '{self.name}' state: CLOSED -> OPEN "
                f"({self.failure_count} failures)"
            )
    
    def reset(self) -> None:
        """Reset the circuit breaker to closed state"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.last_success_time = time.time()
        self.logger.info(f"Circuit breaker '{self.name}' manually reset to CLOSED state")
    
    def get_metrics(self) -> Dict[str, Union[str, int, float]]:
        """Get current metrics for this circuit breaker"""
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'failure_threshold': self.failure_threshold,
            'last_failure_time': self.last_failure_time,
            'last_success_time': self.last_success_time,
            'recovery_timeout': self.recovery_timeout,
            'uptime_seconds': time.time() - self.last_failure_time if self.last_failure_time > 0 else 0
        }