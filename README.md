# 宇诺·跨文件调用追踪引擎 v0.1.0 (社区版)

Copyright (C) 2026 宇诺 (YuNuo)  
作者：赵洪宇 & 诺瓦·迈恩德 (NovaMind)  
许可：MIT License

## 简介

一个轻量级的 Python 跨文件调用关系分析工具。  
使用纯 Python AST 解析，零外部依赖，快速生成项目的调用关系图谱。

## 核心功能

- 🚀 跨文件调用追踪 (Cross-File Call Tracking)
- 📁 文件内调用分析 (Internal Call Analysis)
- 📊 结构化 JSON 报告输出 (Structured JSON Report)
- 🐍 仅依赖 Python 标准库，零第三方依赖

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yuno880/code-tracker.git
cd code-tracker

# 安装为命令行工具（可选）
pip install -e .
