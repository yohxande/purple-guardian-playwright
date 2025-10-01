"""
💜 Monitoring systems for Purple Guardian
"""

import asyncio
import logging
from typing import List, Dict, Any, Set, Optional
from playwright.async_api import Page


class StrictMonitor:
    """
    💜 Strict monitoring system that tracks page state and detects violations
    """

    def __init__(self):
        self.page: Optional[Page] = None
        self.violations: List[Dict[str, Any]] = []
        self.expected_elements: Set[str] = set()
        self.forbidden_elements: Set[str] = set()
        self.logger = logging.getLogger("StrictMonitor")
        
        # Monitoring state
        self.is_monitoring = False
        self.dom_mutations: List[Dict[str, Any]] = []
        self.network_requests: List[Dict[str, Any]] = []
        self.console_messages: List[Dict[str, Any]] = []

    async def setup(self, page: Page):
        """Setup monitoring on the given page"""
        self.page = page
        self.violations.clear()
        self.dom_mutations.clear()
        self.network_requests.clear()
        self.console_messages.clear()
        
        # Setup event listeners
        await self._setup_listeners()
        self.is_monitoring = True
        self.logger.info("💜 Strict monitoring activated")

    async def _setup_listeners(self):
        """Setup all monitoring listeners"""
        # DOM mutation observer
        await self.page.add_init_script("""
            // DOM Mutation Observer
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    window.purpleGuardianMutations = window.purpleGuardianMutations || [];
                    window.purpleGuardianMutations.push({
                        type: mutation.type,
                        target: mutation.target.tagName,
                        addedNodes: mutation.addedNodes.length,
                        removedNodes: mutation.removedNodes.length,
                        timestamp: Date.now()
                    });
                });
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true,
                attributes: true,
                attributeOldValue: true
            });
        """)

        # Network request monitoring
        self.page.on("request", self._on_request)
        self.page.on("response", self._on_response)
        
        # Console message monitoring
        self.page.on("console", self._on_console)
        
        # Page error monitoring
        self.page.on("pageerror", self._on_page_error)

    def _on_request(self, request):
        """Handle network request"""
        self.network_requests.append({
            "type": "request",
            "url": request.url,
            "method": request.method,
            "timestamp": asyncio.get_event_loop().time()
        })

    def _on_response(self, response):
        """Handle network response"""
        self.network_requests.append({
            "type": "response",
            "url": response.url,
            "status": response.status,
            "timestamp": asyncio.get_event_loop().time()
        })

    def _on_console(self, message):
        """Handle console message"""
        self.console_messages.append({
            "type": message.type,
            "text": message.text,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Check for error messages
        if message.type in ["error", "warning"]:
            self._add_violation("console_error", {
                "message": message.text,
                "type": message.type
            })

    def _on_page_error(self, error):
        """Handle page error"""
        self._add_violation("page_error", {
            "message": str(error),
            "timestamp": asyncio.get_event_loop().time()
        })

    async def check_expected_elements(self, selectors: List[str]):
        """Check that expected elements are present"""
        for selector in selectors:
            self.expected_elements.add(selector)
            element = await self.page.query_selector(selector)
            if not element:
                self._add_violation("missing_expected_element", {
                    "selector": selector,
                    "timestamp": asyncio.get_event_loop().time()
                })

    async def check_forbidden_elements(self, selectors: List[str]):
        """Check that forbidden elements are not present"""
        for selector in selectors:
            self.forbidden_elements.add(selector)
            element = await self.page.query_selector(selector)
            if element:
                self._add_violation("forbidden_element_found", {
                    "selector": selector,
                    "timestamp": asyncio.get_event_loop().time()
                })

    async def check_dom_mutations(self) -> List[Dict[str, Any]]:
        """Get DOM mutations that occurred"""
        try:
            mutations = await self.page.evaluate("window.purpleGuardianMutations || []")
            self.dom_mutations.extend(mutations)
            
            # Clear mutations from page
            await self.page.evaluate("window.purpleGuardianMutations = []")
            
            return mutations
        except Exception as e:
            self.logger.warning(f"Failed to check DOM mutations: {e}")
            return []

    def _add_violation(self, violation_type: str, details: Dict[str, Any]):
        """Add a violation to the list"""
        violation = {
            "type": violation_type,
            "details": details,
            "timestamp": asyncio.get_event_loop().time()
        }
        self.violations.append(violation)
        self.logger.warning(f"💜 Violation detected: {violation_type} - {details}")

    def has_violations(self) -> bool:
        """Check if any violations were detected"""
        return len(self.violations) > 0

    def get_violations(self) -> List[Dict[str, Any]]:
        """Get all detected violations"""
        return self.violations.copy()

    def get_dom_mutations(self) -> List[Dict[str, Any]]:
        """Get all DOM mutations"""
        return self.dom_mutations.copy()

    def get_network_requests(self) -> List[Dict[str, Any]]:
        """Get all network requests"""
        return self.network_requests.copy()

    def get_console_messages(self) -> List[Dict[str, Any]]:
        """Get all console messages"""
        return self.console_messages.copy()

    async def validate_state(self):
        """Perform comprehensive state validation"""
        # Check expected elements
        for selector in self.expected_elements:
            await self.check_expected_elements([selector])
        
        # Check forbidden elements
        for selector in self.forbidden_elements:
            await self.check_forbidden_elements([selector])
        
        # Check DOM mutations
        await self.check_dom_mutations()
        
        # Report status
        if self.has_violations():
            self.logger.error(f"💜 State validation failed: {len(self.violations)} violations")
        else:
            self.logger.info("💜 State validation passed")

    def reset(self):
        """Reset monitoring state"""
        self.violations.clear()
        self.dom_mutations.clear()
        self.network_requests.clear()
        self.console_messages.clear()
        self.expected_elements.clear()
        self.forbidden_elements.clear()
        self.is_monitoring = False

    def get_summary(self) -> Dict[str, Any]:
        """Get monitoring summary"""
        return {
            "is_monitoring": self.is_monitoring,
            "violations_count": len(self.violations),
            "dom_mutations_count": len(self.dom_mutations),
            "network_requests_count": len(self.network_requests),
            "console_messages_count": len(self.console_messages),
            "expected_elements": list(self.expected_elements),
            "forbidden_elements": list(self.forbidden_elements)
        }