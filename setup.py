"""Setup configuration for XHS Python SDK."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="xhs-sdk",
    version="0.1.0",
    author="XHS SDK Contributors",
    author_email="",
    description="A Python SDK for XiaoHongShu (小红书) Web API - For Learning Purposes Only",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leeguooooo/xhs-python-sdk",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Topic :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "pylint>=2.17.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
        ],
    },
    package_data={
        "xhs_sdk": ["core/*.js"],
    },
    include_package_data=True,
    keywords="xiaohongshu xhs sdk api learning education",
    project_urls={
        "Bug Reports": "https://github.com/leeguooooo/xhs-python-sdk/issues",
        "Source": "https://github.com/leeguooooo/xhs-python-sdk",
    },
)