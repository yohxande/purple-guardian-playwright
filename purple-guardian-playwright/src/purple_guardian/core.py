"""
💜 Core Purple Guardian implementation
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from playwright.async_api import Browser, BrowserContext, Page

from .workflows import Workflow
from .monitors import StrictMonitor
from .strategies import RestartStrategy
from .config import PurpleConfig
from .detectors import ViolationDetector


class PurpleGuardian:
    """
    💜 Purple Guardian - Zero-tolerance automation framework
    
    The core orchestrator that manages workflow execution with strict monitoring
    and automatic restart capabilities.
    """

    def __init__(
        self,
        config: Optional[PurpleConfig] = None,
        max_retries: int = 3,
        restart_strategy: Optional[RestartStrategy] = None,
        monitor: Optional[StrictMonitor] = None
    ):
        self.config = config or PurpleConfig()
        self.max_retries = max_retries
        self.restart_strategy = restart_strategy or RestartStrategy()
        self.monitor = monitor or StrictMonitor()
        self.violation_detector = ViolationDetector()
        
        self.logger = logging.getLogger("PurpleGuardian")
        self._setup_logging()
        
        # Execution state
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.current_workflow: Optional[Workflow] = None
        
        # Statistics
        self.stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "restart_count": 0,
            "violations_detected": 0
        }

    def _setup_logging(self):
        """Setup logging with purple style"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "💜 %(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    async def run(self, workflow: Workflow) -> Dict[str, Any]:
        """
        Execute workflow with Purple Guardian protection
        
        Args:
            workflow: The workflow to execute
            
        Returns:
            Dict containing execution results and statistics
        """
        self.current_workflow = workflow
        self.stats["total_executions"] += 1
        
        self.logger.info(f"💜 Starting Purple Guardian execution for {workflow.__class__.__name__}")
        
        from . import print_banner
        print_banner()
        
        for attempt in range(self.max_retries + 1):
            try:
                result = await self._execute_attempt(workflow, attempt)
                self.stats["successful_executions"] += 1
                self.logger.info("💜 Workflow completed successfully!")
                return result
                
            except Exception as e:
                self.stats["violations_detected"] += 1
                self.logger.warning(f"💜 Violation detected on attempt {attempt + 1}: {e}")
                
                if attempt < self.max_retries:
                    self.stats["restart_count"] += 1
                    await self._handle_restart(attempt)
                else:
                    self.logger.error("💜 Max retries exceeded. Workflow failed.")
                    raise
        
        return {"status": "failed", "stats": self.stats}

    async def _execute_attempt(self, workflow: Workflow, attempt: int) -> Dict[str, Any]:
        """Execute a single workflow attempt"""
        self.logger.info(f"💜 Attempt {attempt + 1}/{self.max_retries + 1}")
        
        try:
            # Initialize browser environment
            await self._setup_browser()
            
            # Setup monitoring
            await self.monitor.setup(self.page)
            await self.violation_detector.setup(self.page)
            
            # Execute workflow with monitoring
            result = await workflow.execute(self.page)
            
            # Validate final state
            await self._validate_final_state()
            
            return {
                "status": "success",
                "result": result,
                "attempt": attempt + 1,
                "stats": self.stats
            }
            
        finally:
            await self._cleanup_browser()

    async def _setup_browser(self):
        """Setup fresh browser environment"""
        from playwright.async_api import async_playwright
        
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.config.headless,
            args=self.config.browser_args
        )
        
        self.context = await self.browser.new_context(
            viewport=self.config.viewport,
            user_agent=self.config.user_agent
        )
        
        self.page = await self.context.new_page()
        
        # Set timeouts
        self.page.set_default_timeout(self.config.default_timeout)

    async def _cleanup_browser(self):
        """Cleanup browser resources"""
        if self.page:
            await self.page.close()
            self.page = None
            
        if self.context:
            await self.context.close()
            self.context = None
            
        if self.browser:
            await self.browser.close()
            self.browser = None

    async def _handle_restart(self, attempt: int):
        """Handle restart with strategy"""
        self.logger.info("💜 Initiating clean restart...")
        
        # Cleanup current state
        await self._cleanup_browser()
        
        # Apply restart strategy delay
        delay = self.restart_strategy.get_delay(attempt)
        if delay > 0:
            self.logger.info(f"💜 Waiting {delay}s before restart...")
            await asyncio.sleep(delay)

    async def _validate_final_state(self):
        """Validate final execution state"""
        if self.monitor.has_violations():
            violations = self.monitor.get_violations()
            raise Exception(f"Final state violations: {violations}")
        
        if self.violation_detector.has_violations():
            violations = self.violation_detector.get_violations()
            raise Exception(f"Unexpected elements detected: {violations}")

    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return self.stats.copy()

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._cleanup_browser()