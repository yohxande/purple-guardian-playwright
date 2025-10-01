from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="purple-guardian-playwright",
    version="0.1.0",
    author="Yohxande",
    author_email="your-email@example.com",
    description="💜 Zero-tolerance automation framework with Playwright",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yohxande/purple-guardian-playwright",
    project_urls={
        "Bug Tracker": "https://github.com/yohxande/purple-guardian-playwright/issues",
        "Documentation": "https://github.com/yohxande/purple-guardian-playwright/docs",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Playwright",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "purple-guardian=purple_guardian.cli:main",
        ],
    },
)