"""
💜 Workflow base classes and implementations
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from playwright.async_api import Page


class Workflow(ABC):
    """
    💜 Abstract base class for Purple Guardian workflows
    
    All workflows must inherit from this class and implement the execute method.
    """

    def __init__(self, name: Optional[str] = None):
        self.name = name or self.__class__.__name__
        self.state: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}

    @abstractmethod
    async def execute(self, page: Page) -> Any:
        """
        Execute the workflow logic
        
        Args:
            page: Playwright page instance
            
        Returns:
            Any result from the workflow execution
        """
        pass

    async def before_execute(self, page: Page):
        """Hook called before workflow execution"""
        pass

    async def after_execute(self, page: Page, result: Any):
        """Hook called after successful workflow execution"""
        pass

    async def on_violation(self, page: Page, violation: Exception):
        """Hook called when a violation is detected"""
        pass

    def set_state(self, key: str, value: Any):
        """Set workflow state"""
        self.state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get workflow state"""
        return self.state.get(key, default)

    def set_metadata(self, key: str, value: Any):
        """Set workflow metadata"""
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get workflow metadata"""
        return self.metadata.get(key, default)

    def __str__(self) -> str:
        return f"💜 {self.name}"

    def __repr__(self) -> str:
        return f"Workflow(name='{self.name}')"


class BasicWorkflow(Workflow):
    """
    💜 Basic workflow implementation for simple automation tasks
    """

    def __init__(self, url: str, actions: list = None, name: Optional[str] = None):
        super().__init__(name)
        self.url = url
        self.actions = actions or []

    async def execute(self, page: Page) -> Dict[str, Any]:
        """Execute basic workflow with URL navigation and actions"""
        await page.goto(self.url)
        
        results = []
        for action in self.actions:
            if callable(action):
                result = await action(page)
                results.append(result)
            elif isinstance(action, dict):
                result = await self._execute_action(page, action)
                results.append(result)
        
        return {
            "url": self.url,
            "actions_executed": len(self.actions),
            "results": results
        }

    async def _execute_action(self, page: Page, action: Dict[str, Any]):
        """Execute a single action defined as dictionary"""
        action_type = action.get("type")
        
        if action_type == "click":
            await page.click(action["selector"])
            return f"Clicked: {action['selector']}"
        
        elif action_type == "fill":
            await page.fill(action["selector"], action["value"])
            return f"Filled: {action['selector']} = {action['value']}"
        
        elif action_type == "wait":
            if "selector" in action:
                await page.wait_for_selector(action["selector"])
                return f"Waited for: {action['selector']}"
            elif "timeout" in action:
                await page.wait_for_timeout(action["timeout"])
                return f"Waited: {action['timeout']}ms"
        
        elif action_type == "screenshot":
            path = action.get("path", "screenshot.png")
            await page.screenshot(path=path)
            return f"Screenshot saved: {path}"
        
        else:
            raise ValueError(f"Unknown action type: {action_type}")


class FormWorkflow(Workflow):
    """
    💜 Specialized workflow for form interactions
    """

    def __init__(self, url: str, form_data: Dict[str, str], submit_selector: str = "button[type='submit']", name: Optional[str] = None):
        super().__init__(name)
        self.url = url
        self.form_data = form_data
        self.submit_selector = submit_selector

    async def execute(self, page: Page) -> Dict[str, Any]:
        """Execute form workflow"""
        await page.goto(self.url)
        
        # Fill form fields
        filled_fields = []
        for selector, value in self.form_data.items():
            await page.fill(selector, value)
            filled_fields.append(f"{selector} = {value}")
        
        # Submit form
        await page.click(self.submit_selector)
        
        # Wait for navigation or response
        try:
            await page.wait_for_load_state("networkidle", timeout=5000)
        except:
            pass  # Continue if no navigation occurs
        
        return {
            "url": self.url,
            "fields_filled": len(self.form_data),
            "filled_fields": filled_fields,
            "submitted": True,
            "final_url": page.url
        }


class NavigationWorkflow(Workflow):
    """
    💜 Workflow for complex navigation patterns
    """

    def __init__(self, navigation_steps: list, name: Optional[str] = None):
        super().__init__(name)
        self.navigation_steps = navigation_steps

    async def execute(self, page: Page) -> Dict[str, Any]:
        """Execute navigation workflow"""
        visited_urls = []
        
        for step in self.navigation_steps:
            if isinstance(step, str):
                # Simple URL navigation
                await page.goto(step)
                visited_urls.append(step)
            
            elif isinstance(step, dict):
                # Complex navigation step
                if step.get("type") == "goto":
                    await page.goto(step["url"])
                    visited_urls.append(step["url"])
                
                elif step.get("type") == "click_and_wait":
                    await page.click(step["selector"])
                    if "wait_for" in step:
                        await page.wait_for_selector(step["wait_for"])
                    else:
                        await page.wait_for_load_state("networkidle")
                    visited_urls.append(page.url)
        
        return {
            "steps_executed": len(self.navigation_steps),
            "urls_visited": visited_urls,
            "final_url": page.url
        }