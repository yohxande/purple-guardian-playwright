"""
💜 Violation detectors for Purple Guardian
"""

import asyncio
import logging
from typing import List, Dict, Any, Set, Optional, Callable
from playwright.async_api import Page


class ViolationDetector:
    """
    💜 Advanced violation detection system
    
    Detects unexpected elements, behaviors, and violations in web applications.
    """

    def __init__(self):
        self.page: Optional[Page] = None
        self.violations: List[Dict[str, Any]] = []
        self.logger = logging.getLogger("ViolationDetector")
        
        # Detection rules
        self.unexpected_selectors: Set[str] = set()
        self.prohibited_texts: Set[str] = set()
        self.required_elements: Set[str] = set()
        self.custom_validators: List[Callable] = []
        
        # Detection state
        self.is_active = False
        self.detection_history: List[Dict[str, Any]] = []

    async def setup(self, page: Page):
        """Setup violation detection on the given page"""
        self.page = page
        self.violations.clear()
        self.detection_history.clear()
        
        # Setup default detection rules
        await self._setup_default_rules()
        
        self.is_active = True
        self.logger.info("💜 Violation detector activated")

    async def _setup_default_rules(self):
        """Setup default violation detection rules"""
        # Common unexpected elements that indicate errors
        self.unexpected_selectors.update([
            ".error",
            ".alert-danger",
            ".error-message",
            "[role='alert']",
            ".notification.error",
            ".toast.error",
            ".modal.error",
            "#error",
            ".exception",
            ".stack-trace"
        ])
        
        # Common error texts
        self.prohibited_texts.update([
            "404 Not Found",
            "500 Internal Server Error",
            "Access Denied",
            "Unauthorized",
            "Forbidden",
            "Something went wrong",
            "An error occurred",
            "Error:",
            "Exception:",
            "Stack trace",
            "Failed to load",
            "Connection timeout",
            "Service unavailable"
        ])

    async def detect_violations(self) -> List[Dict[str, Any]]:
        """
        Perform comprehensive violation detection
        
        Returns:
            List of detected violations
        """
        if not self.is_active or not self.page:
            return []

        current_violations = []
        
        try:
            # Check for unexpected elements
            unexpected_violations = await self._check_unexpected_elements()
            current_violations.extend(unexpected_violations)
            
            # Check for prohibited text content
            text_violations = await self._check_prohibited_texts()
            current_violations.extend(text_violations)
            
            # Check for required elements
            missing_violations = await self._check_required_elements()
            current_violations.extend(missing_violations)
            
            # Run custom validators
            custom_violations = await self._run_custom_validators()
            current_violations.extend(custom_violations)
            
            # Check page state
            state_violations = await self._check_page_state()
            current_violations.extend(state_violations)
            
            # Record all violations
            for violation in current_violations:
                self._record_violation(violation)
            
            return current_violations
            
        except Exception as e:
            self.logger.error(f"💜 Error during violation detection: {e}")
            return []

    async def _check_unexpected_elements(self) -> List[Dict[str, Any]]:
        """Check for unexpected elements on the page"""
        violations = []
        
        for selector in self.unexpected_selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                for element in elements:
                    # Get element text and attributes for context
                    text = await element.text_content()
                    tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
                    
                    violations.append({
                        "type": "unexpected_element",
                        "selector": selector,
                        "tag_name": tag_name,
                        "text": text[:200] if text else "",  # Limit text length
                        "timestamp": asyncio.get_event_loop().time()
                    })
                    
            except Exception as e:
                self.logger.debug(f"Error checking selector {selector}: {e}")
        
        return violations

    async def _check_prohibited_texts(self) -> List[Dict[str, Any]]:
        """Check for prohibited text content"""
        violations = []
        
        try:
            page_content = await self.page.content()
            page_text = await self.page.evaluate("document.body.textContent")
            
            for prohibited_text in self.prohibited_texts:
                if prohibited_text.lower() in page_text.lower():
                    violations.append({
                        "type": "prohibited_text",
                        "text": prohibited_text,
                        "found_in": "page_content",
                        "timestamp": asyncio.get_event_loop().time()
                    })
                    
        except Exception as e:
            self.logger.debug(f"Error checking prohibited texts: {e}")
        
        return violations

    async def _check_required_elements(self) -> List[Dict[str, Any]]:
        """Check for required elements that should be present"""
        violations = []
        
        for selector in self.required_elements:
            try:
                element = await self.page.query_selector(selector)
                if not element:
                    violations.append({
                        "type": "missing_required_element",
                        "selector": selector,
                        "timestamp": asyncio.get_event_loop().time()
                    })
                    
            except Exception as e:
                self.logger.debug(f"Error checking required element {selector}: {e}")
        
        return violations

    async def _run_custom_validators(self) -> List[Dict[str, Any]]:
        """Run custom validation functions"""
        violations = []
        
        for validator in self.custom_validators:
            try:
                result = await validator(self.page)
                if result:
                    if isinstance(result, dict):
                        violations.append(result)
                    elif isinstance(result, list):
                        violations.extend(result)
                    else:
                        violations.append({
                            "type": "custom_validation_failure",
                            "result": str(result),
                            "validator": validator.__name__,
                            "timestamp": asyncio.get_event_loop().time()
                        })
                        
            except Exception as e:
                violations.append({
                    "type": "custom_validator_error",
                    "error": str(e),
                    "validator": validator.__name__,
                    "timestamp": asyncio.get_event_loop().time()
                })
        
        return violations

    async def _check_page_state(self) -> List[Dict[str, Any]]:
        """Check overall page state for violations"""
        violations = []
        
        try:
            # Check if page is still loading
            ready_state = await self.page.evaluate("document.readyState")
            if ready_state != "complete":
                violations.append({
                    "type": "page_not_ready",
                    "ready_state": ready_state,
                    "timestamp": asyncio.get_event_loop().time()
                })
            
            # Check for JavaScript errors in console
            # Note: Console errors are typically caught by monitors, but we double-check here
            
            # Check for broken images
            broken_images = await self.page.evaluate("""
                Array.from(document.images).filter(img => !img.complete || img.naturalWidth === 0).length
            """)
            
            if broken_images > 0:
                violations.append({
                    "type": "broken_images",
                    "count": broken_images,
                    "timestamp": asyncio.get_event_loop().time()
                })
                
        except Exception as e:
            self.logger.debug(f"Error checking page state: {e}")
        
        return violations

    def _record_violation(self, violation: Dict[str, Any]):
        """Record a violation in the history"""
        self.violations.append(violation)
        self.detection_history.append(violation)
        
        self.logger.warning(f"💜 Violation detected: {violation['type']} - {violation}")

    def add_unexpected_selector(self, selector: str):
        """Add a selector that should not appear on the page"""
        self.unexpected_selectors.add(selector)
        self.logger.info(f"💜 Added unexpected selector: {selector}")

    def add_prohibited_text(self, text: str):
        """Add text that should not appear on the page"""
        self.prohibited_texts.add(text)
        self.logger.info(f"💜 Added prohibited text: {text}")

    def add_required_element(self, selector: str):
        """Add a selector that must be present on the page"""
        self.required_elements.add(selector)
        self.logger.info(f"💜 Added required element: {selector}")

    def add_custom_validator(self, validator: Callable):
        """Add a custom validation function"""
        self.custom_validators.append(validator)
        self.logger.info(f"💜 Added custom validator: {validator.__name__}")

    def remove_unexpected_selector(self, selector: str):
        """Remove an unexpected selector"""
        self.unexpected_selectors.discard(selector)

    def remove_prohibited_text(self, text: str):
        """Remove a prohibited text"""
        self.prohibited_texts.discard(text)

    def remove_required_element(self, selector: str):
        """Remove a required element"""
        self.required_elements.discard(selector)

    def has_violations(self) -> bool:
        """Check if any violations were detected"""
        return len(self.violations) > 0

    def get_violations(self) -> List[Dict[str, Any]]:
        """Get all detected violations"""
        return self.violations.copy()

    def get_violation_summary(self) -> Dict[str, Any]:
        """Get summary of detected violations"""
        violation_counts = {}
        for violation in self.violations:
            violation_type = violation.get("type", "unknown")
            violation_counts[violation_type] = violation_counts.get(violation_type, 0) + 1
        
        return {
            "total_violations": len(self.violations),
            "violation_types": violation_counts,
            "is_active": self.is_active,
            "rules_count": {
                "unexpected_selectors": len(self.unexpected_selectors),
                "prohibited_texts": len(self.prohibited_texts),
                "required_elements": len(self.required_elements),
                "custom_validators": len(self.custom_validators)
            }
        }

    def reset(self):
        """Reset violation detector state"""
        self.violations.clear()
        self.detection_history.clear()
        self.is_active = False

    def clear_rules(self):
        """Clear all detection rules"""
        self.unexpected_selectors.clear()
        self.prohibited_texts.clear()
        self.required_elements.clear()
        self.custom_validators.clear()
        self.logger.info("💜 All detection rules cleared")