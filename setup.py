#!/usr/bin/env python3
from setuptools import setup

setup(
    name="code-tracker",
    version="0.1.0",
    description="宇诺·跨文件调用追踪引擎 (社区版)",
    author="赵洪宇 & 诺瓦·迈恩德 (NovaMind)",
    url="https://github.com/你的用户名/code-tracker",
    py_modules=["code_tracker"],
    entry_points={
        "console_scripts": [
            "code-tracker=code_tracker:main",
        ],
    },
    python_requires=">=3.9",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
