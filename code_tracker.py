#!/usr/bin/env python3
"""
跨文件调用追踪引擎 v0.1.0 (社区版)
Copyright (C) 2026 宇诺 (YuNuo)
作者：赵洪宇 & 诺瓦·迈恩德 (NovaMind)
许可：MIT License
"""
import ast
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class CodeTracker:
    """轻量级跨文件调用关系分析器"""

    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.class_index: Dict[str, str] = {}
        self.file_var_map: Dict[str, Dict[str, str]] = {}
        self.call_graph: Dict[str, Dict[str, List[str]]] = {}
        self.total_classes = 0
        self.total_funcs = 0
        self.total_relations = 0

    def build(self):
        """主入口：构建完整的跨文件调用知识图谱"""
        self._phase1_build_index()
        self._phase2_analyze_calls()
        return self

    def _phase1_build_index(self):
        """第一阶段：遍历所有文件，建立类名索引和变量映射"""
        for py_file in self.project_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
            except (SyntaxError, UnicodeDecodeError):
                continue

            var_to_class: Dict[str, str] = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self.class_index[node.name] = py_file.name
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if (isinstance(target, ast.Attribute) and
                            isinstance(target.value, ast.Name) and
                            target.value.id == 'self' and
                            isinstance(node.value, ast.Call) and
                            isinstance(node.value.func, ast.Name)):
                            var_to_class[target.attr] = node.value.func.id
            self.file_var_map[py_file.name] = var_to_class

    def _phase2_analyze_calls(self):
        """第二阶段：分析每个文件内部的函数调用关系，并解析跨文件调用"""
        for py_file in self.project_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
            except (SyntaxError, UnicodeDecodeError):
                continue

            funcs_in_file = 0
            classes_in_file = 0
            file_functions: Dict[str, List[str]] = {}

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes_in_file += 1
                    self.total_classes += 1
                elif isinstance(node, ast.FunctionDef):
                    funcs_in_file += 1
                    self.total_funcs += 1
                    file_functions[node.name] = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    current_func = node.name
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Name):
                                called_name = child.func.id
                                if called_name in file_functions or called_name != current_func:
                                    file_functions[current_func].append(called_name)
                            elif isinstance(child.func, ast.Attribute):
                                attr_name = child.func.attr
                                non_function_attrs = {
                                    'time', 'info', 'debug', 'error', 'warning',
                                    'logger', 'conn', 'cursor', 'running', 'lock',
                                    'config', 'data', 'path', 'name', 'version'
                                }
                                if attr_name in non_function_attrs:
                                    continue

                                call_str = f"self.{attr_name}"
                                if isinstance(child.func.value, ast.Attribute):
                                    proxy_name = child.func.value.attr
                                    current_var_map = self.file_var_map.get(py_file.name, {})
                                    class_name = current_var_map.get(proxy_name, proxy_name)
                                    if class_name in self.class_index:
                                        source_file = self.class_index[class_name]
                                        call_str = f"{source_file}:{attr_name}"
                                file_functions[current_func].append(call_str)

            self.call_graph[py_file.name] = file_functions
            print(f"  ✅ {py_file.name}: {classes_in_file}个类, {funcs_in_file}个函数")

    def report(self) -> Dict:
        """生成结构化分析报告"""
        cross_file_calls: List[Tuple[str, str, str]] = []
        internal_calls: List[Tuple[str, str, str]] = []

        for file_name, funcs in self.call_graph.items():
            for func_name, calls in funcs.items():
                if calls:
                    unique_calls = list(set(calls))
                    for call in unique_calls:
                        if '.py:' in call:
                            cross_file_calls.append((file_name, func_name, call))
                        else:
                            internal_calls.append((file_name, func_name, call))

        return {
            "summary": {
                "total_files": len(self.call_graph),
                "total_classes": self.total_classes,
                "total_funcs": self.total_funcs,
                "cross_file_calls": len(cross_file_calls),
                "internal_calls": len(internal_calls)
            },
            "cross_file_calls": [
                {"source_file": f, "source_func": n, "target": c}
                for f, n, c in cross_file_calls
            ],
            "internal_calls": [
                {"source_file": f, "source_func": n, "target": c}
                for f, n, c in internal_calls
            ]
        }

    def print_report(self):
        """控制台输出可视化报告"""
        data = self.report()
        s = data["summary"]
        print(f"\n{'='*50}")
        print(f"📊 跨文件调用追踪报告")
        print(f"{'='*50}")
        print(f"  扫描文件: {s['total_files']} 个")
        print(f"  类总数:   {s['total_classes']} 个")
        print(f"  函数总数: {s['total_funcs']} 个")
        print(f"  跨文件调用: {s['cross_file_calls']} 条")
        print(f"  文件内调用: {s['internal_calls']} 条")

        if data["cross_file_calls"]:
            print(f"\n📡 跨文件调用关系：")
            for item in data["cross_file_calls"][:30]:
                print(f"  {item['source_file']}:{item['source_func']}() → {item['target']}")

        if data["internal_calls"]:
            print(f"\n📁 文件内调用关系（共 {s['internal_calls']} 条，显示前10条）：")
            for item in data["internal_calls"][:10]:
                print(f"  {item['source_file']}:{item['source_func']}() → {item['target']}")


def main():
    if len(sys.argv) < 2:
        print("用法: python3 code_tracker.py <项目目录路径>")
        sys.exit(1)

    project_dir = sys.argv[1]
    tracker = CodeTracker(project_dir)
    tracker.build()
    tracker.print_report()


if __name__ == "__main__":
    main()
