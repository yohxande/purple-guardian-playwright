# 💜 Purple Guardian Playwright

[![Python](https://img.shields.io/badge/Python-3.8+-purple.svg)](https://www.python.org)
[![Playwright](https://img.shields.io/badge/Playwright-1.40+-purple.svg)](https://playwright.dev)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Love](https://img.shields.io/badge/Made%20with-💜-purple.svg)](https://github.com/yohxande)

Zero-tolerance automation framework with automatic restart on unexpected elements.

## 💜 Features

- 🛡️ **Zero Tolerance**: Restart workflow on any unexpected element
- 🔄 **Smart Restart**: Automatic retry with exponential backoff
- 📊 **Comprehensive Monitoring**: Track all DOM mutations, AJAX calls
- 🎯 **Strict Validation**: Define expected elements explicitly
- 💜 **Purple Philosophy**: Clean execution over dirty workarounds

## 🚀 Quick Start

```python
from purple_guardian import PurpleGuardian, Workflow

class MyWorkflow(Workflow):
    async def execute(self, page):
        await page.goto("https://example.com")
        await page.fill("#username", "user")
        await page.click("button[type='submit']")

async def main():
    guardian = PurpleGuardian(max_retries=3)
    await guardian.run(MyWorkflow())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## 📦 Installation

```bash
pip install purple-guardian-playwright
```

Or install from source:

```bash
git clone https://github.com/yohxande/purple-guardian-playwright.git
cd purple-guardian-playwright
pip install -e .
```

## 💜 Philosophy

> "Perfect execution or clean restart. No compromise."

This framework embraces:

- **Predictability** over adaptability
- **Clean state** over error recovery
- **Strict boundaries** over flexibility

## 🔧 Configuration

### Basic Configuration

```python
from purple_guardian import PurpleGuardian, PurpleConfig

config = PurpleConfig(
    headless=False,
    max_retries=3,
    screenshot_on_violation=True
)

guardian = PurpleGuardian(config=config)
```

### Environment Variables

```bash
export PURPLE_HEADLESS=true
export PURPLE_MAX_RETRIES=5
export PURPLE_DEFAULT_TIMEOUT=30000
```

### Configuration from File

```python
config = PurpleConfig.from_file("config.json")
guardian = PurpleGuardian(config=config)
```

## 🛡️ Monitoring & Detection

### Strict Monitoring

```python
from purple_guardian import StrictMonitor

monitor = StrictMonitor()
await monitor.check_expected_elements(["#submit-button", ".success-message"])
await monitor.check_forbidden_elements([".error", ".alert-danger"])
```

### Violation Detection

```python
from purple_guardian import ViolationDetector

detector = ViolationDetector()
detector.add_unexpected_selector(".error")
detector.add_prohibited_text("Something went wrong")
detector.add_required_element("#main-content")
```

## 🔄 Restart Strategies

### Built-in Strategies

```python
from purple_guardian import RestartStrategy, RestartType

# Exponential backoff (default)
strategy = RestartStrategy.create_exponential(base_delay=1.0, backoff_factor=2.0)

# Linear delay
strategy = RestartStrategy.create_linear(base_delay=2.0)

# Custom delays
strategy = RestartStrategy.create_custom([1, 3, 5, 10])

guardian = PurpleGuardian(restart_strategy=strategy)
```

## 📋 Workflow Types

### Basic Workflow

```python
from purple_guardian import BasicWorkflow

workflow = BasicWorkflow(
    url="https://example.com",
    actions=[
        {"type": "fill", "selector": "#username", "value": "user"},
        {"type": "click", "selector": "#login-button"},
        {"type": "wait", "selector": ".dashboard"}
    ]
)
```

### Form Workflow

```python
from purple_guardian import FormWorkflow

workflow = FormWorkflow(
    url="https://example.com/login",
    form_data={
        "#username": "user",
        "#password": "pass"
    },
    submit_selector="#login-button"
)
```

### Navigation Workflow

```python
from purple_guardian import NavigationWorkflow

workflow = NavigationWorkflow([
    "https://example.com",
    {"type": "click_and_wait", "selector": "#next-page", "wait_for": ".content"},
    "https://example.com/final-page"
])
```

## 🧪 Testing

Run tests with:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=purple_guardian tests/
```

## 📊 Examples

Check out the [examples](examples/) directory for more usage patterns:

- [Basic Example](examples/basic_example.py) - Simple workflow automation
- [Advanced Example](examples/advanced_example.py) - Complex scenarios with monitoring
- [Custom Workflow](examples/custom_workflow.py) - Building custom workflows

## 📖 Documentation

- [Getting Started](docs/getting_started.md)
- [API Reference](docs/api_reference.md)
- [Best Practices](docs/best_practices.md)
- [Configuration Guide](docs/configuration.md)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💜 Author

Created with 💜 by [Yohxande](https://github.com/yohxande)

## 🌟 Acknowledgments

- Built with [Playwright](https://playwright.dev/)
- Inspired by zero-tolerance testing principles
- Powered by love and purple energy 💜

---

_"Built with love, powered by purple"_ 💜

## 📈 Roadmap

- [ ] Web UI for monitoring
- [ ] Integration with popular CI/CD tools
- [ ] Visual regression testing
- [ ] AI-powered element detection
- [ ] Performance monitoring
- [ ] Real-time dashboard

## 🐛 Known Issues

- Playwright dependency requires additional setup for some environments
- Screenshots may consume significant disk space in high-volume scenarios

## 💡 Tips

1. **Start with development config** for debugging
2. **Use custom validators** for complex scenarios
3. **Monitor violations** to understand failure patterns
4. **Adjust restart strategies** based on your application's behavior
5. **Enable screenshots** for easier debugging

## 🔗 Related Projects

- [Playwright](https://playwright.dev/) - Modern web testing framework
- [Selenium](https://selenium.dev/) - Web automation framework
- [Puppeteer](https://pptr.dev/) - Node.js API for Chrome
