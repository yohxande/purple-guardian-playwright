"""
💜 Test cases for Purple Guardian core functionality
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

# Note: These imports will work after the package is installed
try:
    from purple_guardian import PurpleGuardian, Workflow, PurpleConfig
    from purple_guardian.monitors import StrictMonitor
    from purple_guardian.strategies import RestartStrategy
except ImportError:
    # Skip tests if package not installed
    pytest.skip("purple_guardian not installed", allow_module_level=True)


class TestWorkflow(Workflow):
    """Test workflow for unit tests"""
    
    def __init__(self, should_fail=False):
        super().__init__("TestWorkflow")
        self.should_fail = should_fail
        self.executed = False
    
    async def execute(self, page):
        self.executed = True
        if self.should_fail:
            raise Exception("Test failure")
        return {"status": "success", "test": True}


@pytest.fixture
def config():
    """Test configuration"""
    return PurpleConfig(
        headless=True,
        max_retries=2,
        screenshot_on_violation=False
    )


@pytest.fixture
def guardian(config):
    """Purple Guardian instance for testing"""
    return PurpleGuardian(config=config)


@pytest.mark.asyncio
async def test_successful_workflow(guardian):
    """Test successful workflow execution"""
    workflow = TestWorkflow(should_fail=False)
    
    # Mock browser setup
    guardian._setup_browser = AsyncMock()
    guardian._cleanup_browser = AsyncMock()
    guardian.page = MagicMock()
    guardian.monitor = MagicMock()
    guardian.monitor.setup = AsyncMock()
    guardian.monitor.has_violations = MagicMock(return_value=False)
    guardian.violation_detector = MagicMock()
    guardian.violation_detector.setup = AsyncMock()
    guardian.violation_detector.has_violations = MagicMock(return_value=False)
    
    result = await guardian.run(workflow)
    
    assert result["status"] == "success"
    assert workflow.executed
    assert guardian.stats["successful_executions"] == 1


@pytest.mark.asyncio
async def test_workflow_with_retries(guardian):
    """Test workflow with failures and retries"""
    guardian.max_retries = 1
    workflow = TestWorkflow(should_fail=True)
    
    # Mock browser setup
    guardian._setup_browser = AsyncMock()
    guardian._cleanup_browser = AsyncMock()
    guardian._handle_restart = AsyncMock()
    
    with pytest.raises(Exception):
        await guardian.run(workflow)
    
    assert guardian.stats["restart_count"] == 1
    assert guardian.stats["violations_detected"] == 2  # Initial + 1 retry


def test_config_validation():
    """Test configuration validation"""
    # Valid config
    config = PurpleConfig(max_retries=3, default_timeout=5000)
    assert config.max_retries == 3
    
    # Invalid config
    with pytest.raises(ValueError):
        PurpleConfig(max_retries=-1)
    
    with pytest.raises(ValueError):
        PurpleConfig(default_timeout=500)  # Too low


def test_restart_strategy():
    """Test restart strategy calculations"""
    strategy = RestartStrategy.create_exponential(base_delay=1.0, backoff_factor=2.0)
    
    # Test delay calculations
    assert strategy.get_delay(0) >= 1.0
    assert strategy.get_delay(1) >= 2.0
    assert strategy.get_delay(2) >= 4.0


def test_config_from_env(monkeypatch):
    """Test configuration from environment variables"""
    monkeypatch.setenv("PURPLE_HEADLESS", "false")
    monkeypatch.setenv("PURPLE_MAX_RETRIES", "5")
    
    config = PurpleConfig.from_env()
    assert config.headless == False
    assert config.max_retries == 5


@pytest.mark.asyncio
async def test_monitor_setup():
    """Test monitor setup and violation detection"""
    monitor = StrictMonitor()
    
    # Mock page
    page = MagicMock()
    page.add_init_script = AsyncMock()
    page.on = MagicMock()
    
    await monitor.setup(page)
    
    assert monitor.is_monitoring
    assert monitor.page == page


def test_guardian_statistics():
    """Test statistics tracking"""
    guardian = PurpleGuardian()
    
    # Initial stats
    stats = guardian.get_stats()
    assert stats["total_executions"] == 0
    assert stats["successful_executions"] == 0
    
    # After execution (simulated)
    guardian.stats["total_executions"] = 1
    guardian.stats["successful_executions"] = 1
    
    stats = guardian.get_stats()
    assert stats["total_executions"] == 1
    assert stats["successful_executions"] == 1


if __name__ == "__main__":
    pytest.main([__file__])