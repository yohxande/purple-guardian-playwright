"""
💜 Restart strategies for Purple Guardian
"""

import asyncio
import logging
import random
from typing import Dict, Any, Optional
from enum import Enum


class RestartType(Enum):
    """Types of restart strategies"""
    IMMEDIATE = "immediate"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    RANDOM = "random"
    CUSTOM = "custom"


class RestartStrategy:
    """
    💜 Restart strategy manager for Purple Guardian
    
    Handles different restart timing and backoff strategies when violations occur.
    """

    def __init__(
        self,
        strategy_type: RestartType = RestartType.EXPONENTIAL,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        custom_delays: Optional[list] = None
    ):
        self.strategy_type = strategy_type
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.custom_delays = custom_delays or []
        
        self.logger = logging.getLogger("RestartStrategy")
        
        # Statistics
        self.restart_count = 0
        self.total_delay_time = 0.0
        self.restart_history: list = []

    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay before restart based on strategy
        
        Args:
            attempt: Current attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        delay = self._calculate_base_delay(attempt)
        
        # Apply jitter if enabled
        if self.jitter:
            delay = self._apply_jitter(delay)
        
        # Ensure delay doesn't exceed maximum
        delay = min(delay, self.max_delay)
        
        # Record statistics
        self.restart_count += 1
        self.total_delay_time += delay
        self.restart_history.append({
            "attempt": attempt,
            "delay": delay,
            "strategy": self.strategy_type.value,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        self.logger.info(f"💜 Restart delay calculated: {delay:.2f}s (attempt {attempt + 1})")
        return delay

    def _calculate_base_delay(self, attempt: int) -> float:
        """Calculate base delay without jitter"""
        if self.strategy_type == RestartType.IMMEDIATE:
            return 0.0
        
        elif self.strategy_type == RestartType.LINEAR:
            return self.base_delay * (attempt + 1)
        
        elif self.strategy_type == RestartType.EXPONENTIAL:
            return self.base_delay * (self.backoff_factor ** attempt)
        
        elif self.strategy_type == RestartType.RANDOM:
            return random.uniform(self.base_delay, self.base_delay * 5)
        
        elif self.strategy_type == RestartType.CUSTOM:
            if attempt < len(self.custom_delays):
                return self.custom_delays[attempt]
            else:
                # Use last delay or exponential fallback
                return self.custom_delays[-1] if self.custom_delays else self.base_delay
        
        else:
            return self.base_delay

    def _apply_jitter(self, delay: float) -> float:
        """Apply random jitter to delay"""
        # Add up to 20% random variation
        jitter_amount = delay * 0.2
        return delay + random.uniform(-jitter_amount, jitter_amount)

    async def wait(self, attempt: int):
        """
        Perform the actual wait with the calculated delay
        
        Args:
            attempt: Current attempt number
        """
        delay = self.get_delay(attempt)
        
        if delay > 0:
            self.logger.info(f"💜 Waiting {delay:.2f}s before restart...")
            
            # Show countdown for longer delays
            if delay > 5:
                await self._countdown_wait(delay)
            else:
                await asyncio.sleep(delay)

    async def _countdown_wait(self, delay: float, interval: float = 1.0):
        """Wait with countdown display"""
        remaining = delay
        
        while remaining > 0:
            if remaining >= interval:
                self.logger.info(f"💜 Restarting in {remaining:.0f}s...")
                await asyncio.sleep(interval)
                remaining -= interval
            else:
                await asyncio.sleep(remaining)
                remaining = 0

    def reset_statistics(self):
        """Reset restart statistics"""
        self.restart_count = 0
        self.total_delay_time = 0.0
        self.restart_history.clear()

    def get_statistics(self) -> Dict[str, Any]:
        """Get restart strategy statistics"""
        return {
            "strategy_type": self.strategy_type.value,
            "restart_count": self.restart_count,
            "total_delay_time": self.total_delay_time,
            "average_delay": self.total_delay_time / max(1, self.restart_count),
            "restart_history": self.restart_history.copy(),
            "config": {
                "base_delay": self.base_delay,
                "max_delay": self.max_delay,
                "backoff_factor": self.backoff_factor,
                "jitter": self.jitter
            }
        }

    def adjust_parameters(
        self,
        base_delay: Optional[float] = None,
        max_delay: Optional[float] = None,
        backoff_factor: Optional[float] = None,
        jitter: Optional[bool] = None
    ):
        """Dynamically adjust strategy parameters"""
        if base_delay is not None:
            self.base_delay = base_delay
            self.logger.info(f"💜 Base delay adjusted to {base_delay}s")
        
        if max_delay is not None:
            self.max_delay = max_delay
            self.logger.info(f"💜 Max delay adjusted to {max_delay}s")
        
        if backoff_factor is not None:
            self.backoff_factor = backoff_factor
            self.logger.info(f"💜 Backoff factor adjusted to {backoff_factor}")
        
        if jitter is not None:
            self.jitter = jitter
            self.logger.info(f"💜 Jitter {'enabled' if jitter else 'disabled'}")

    @classmethod
    def create_immediate(cls):
        """Create immediate restart strategy (no delay)"""
        return cls(strategy_type=RestartType.IMMEDIATE)

    @classmethod
    def create_linear(cls, base_delay: float = 2.0, max_delay: float = 30.0):
        """Create linear backoff strategy"""
        return cls(
            strategy_type=RestartType.LINEAR,
            base_delay=base_delay,
            max_delay=max_delay
        )

    @classmethod
    def create_exponential(cls, base_delay: float = 1.0, backoff_factor: float = 2.0, max_delay: float = 60.0):
        """Create exponential backoff strategy"""
        return cls(
            strategy_type=RestartType.EXPONENTIAL,
            base_delay=base_delay,
            backoff_factor=backoff_factor,
            max_delay=max_delay
        )

    @classmethod
    def create_random(cls, base_delay: float = 1.0, max_delay: float = 30.0):
        """Create random delay strategy"""
        return cls(
            strategy_type=RestartType.RANDOM,
            base_delay=base_delay,
            max_delay=max_delay
        )

    @classmethod
    def create_custom(cls, delays: list):
        """Create custom delay strategy with predefined delays"""
        return cls(
            strategy_type=RestartType.CUSTOM,
            custom_delays=delays
        )

    def __str__(self) -> str:
        return f"💜 RestartStrategy({self.strategy_type.value})"

    def __repr__(self) -> str:
        return f"RestartStrategy(type={self.strategy_type.value}, base_delay={self.base_delay}, max_delay={self.max_delay})"