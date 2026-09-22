#!/usr/bin/env python3
"""
Vue 2 to Vue 3 Migration Analyzer
Scans Vue 2 project files and identifies migration points.
"""

import os
import re
import sys
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class MigrationIssue:
    file: str
    line: int
    category: str
    severity: str  # 'breaking', 'warning', 'info'
    description: str
    suggestion: str


@dataclass
class AnalysisReport:
    total_files: int = 0
    vue_files: int = 0
    js_files: int = 0
    issues: List[MigrationIssue] = field(default_factory=list)

    def add_issue(self, issue: MigrationIssue):
        self.issues.append(issue)

    def to_dict(self) -> Dict:
        return {
            "summary": {
                "total_files": self.total_files,
                "vue_files": self.vue_files,
                "js_files": self.js_files,
                "breaking_changes": len([i for i in self.issues if i.severity == 'breaking']),
                "warnings": len([i for i in self.issues if i.severity == 'warning']),
                "info": len([i for i in self.issues if i.severity == 'info']),
            },
            "issues": [
                {
                    "file": i.file,
                    "line": i.line,
                    "category": i.category,
                    "severity": i.severity,
                    "description": i.description,
                    "suggestion": i.suggestion
                }
                for i in self.issues
            ]
        }


# Vue 2 patterns that need migration
PATTERNS = {
    # Lifecycle hooks
    "beforeDestroy": {
        "pattern": r"\bbeforeDestroy\s*[:(]",
        "category": "lifecycle",
        "severity": "breaking",
        "description": "beforeDestroy is renamed to beforeUnmount in Vue 3",
        "suggestion": "Replace with beforeUnmount"
    },
    "destroyed": {
        "pattern": r"\bdestroyed\s*[:(]",
        "category": "lifecycle",
        "severity": "breaking",
        "description": "destroyed is renamed to unmounted in Vue 3",
        "suggestion": "Replace with unmounted"
    },

    # Filters (removed in Vue 3)
    "filters": {
        "pattern": r"\bfilters\s*:\s*\{",
        "category": "filters",
        "severity": "breaking",
        "description": "Filters are removed in Vue 3",
        "suggestion": "Use computed properties or methods instead"
    },
    "pipe_filter": {
        "pattern": r"\{\{\s*\w+\s*\|\s*\w+",
        "category": "filters",
        "severity": "breaking",
        "description": "Filter syntax (|) in templates is removed in Vue 3",
        "suggestion": "Use computed properties or method calls instead"
    },

    # $listeners (removed)
    "$listeners": {
        "pattern": r"\$listeners",
        "category": "breaking-api",
        "severity": "breaking",
        "description": "$listeners is removed in Vue 3, merged into $attrs",
        "suggestion": "Use $attrs instead, listeners are now part of $attrs"
    },

    # $children (removed)
    "$children": {
        "pattern": r"\$children",
        "category": "breaking-api",
        "severity": "breaking",
        "description": "$children is removed in Vue 3",
        "suggestion": "Use template refs or provide/inject instead"
    },

    # $scopedSlots (removed)
    "$scopedSlots": {
        "pattern": r"\$scopedSlots",
        "category": "slots",
        "severity": "breaking",
        "description": "$scopedSlots is removed in Vue 3",
        "suggestion": "Use $slots instead, all slots are now functions"
    },

    # .sync modifier (removed)
    "sync_modifier": {
        "pattern": r"\.sync\b",
        "category": "v-model",
        "severity": "breaking",
        "description": ".sync modifier is removed in Vue 3",
        "suggestion": "Use v-model with argument: v-model:propName"
    },

    # v-model on custom component
    "v-model_value": {
        "pattern": r"(?:props|model)\s*:.*['\"]value['\"]",
        "category": "v-model",
        "severity": "warning",
        "description": "v-model prop name changed from 'value' to 'modelValue' in Vue 3",
        "suggestion": "Rename to 'modelValue' and event to 'update:modelValue'"
    },

    # $on, $off, $once (removed)
    "$on_eventbus": {
        "pattern": r"\$on\s*\(",
        "category": "events",
        "severity": "breaking",
        "description": "$on is removed in Vue 3, event bus pattern no longer works",
        "suggestion": "Use mitt or tiny-emitter library, or provide/inject"
    },
    "$off_eventbus": {
        "pattern": r"\$off\s*\(",
        "category": "events",
        "severity": "breaking",
        "description": "$off is removed in Vue 3",
        "suggestion": "Use mitt or tiny-emitter library, or provide/inject"
    },
    "$once_eventbus": {
        "pattern": r"\$once\s*\(",
        "category": "events",
        "severity": "breaking",
        "description": "$once is removed in Vue 3",
        "suggestion": "Use mitt or tiny-emitter library, or provide/inject"
    },

    # Vue.set / this.$set (removed)
    "vue_set": {
        "pattern": r"(?:Vue|\$)\.set\s*\(",
        "category": "reactivity",
        "severity": "breaking",
        "description": "Vue.set/$set is removed in Vue 3 (no longer needed with Proxy)",
        "suggestion": "Directly assign the property, Vue 3 reactivity handles it"
    },
    "vue_delete": {
        "pattern": r"(?:Vue|\$)\.delete\s*\(",
        "category": "reactivity",
        "severity": "breaking",
        "description": "Vue.delete/$delete is removed in Vue 3",
        "suggestion": "Use delete operator directly"
    },

    # Vue.extend (removed)
    "vue_extend": {
        "pattern": r"Vue\.extend\s*\(",
        "category": "global-api",
        "severity": "breaking",
        "description": "Vue.extend is removed in Vue 3",
        "suggestion": "Use defineComponent or plain object"
    },

    # Vue.component global registration
    "vue_component_global": {
        "pattern": r"Vue\.component\s*\(",
        "category": "global-api",
        "severity": "breaking",
        "description": "Global Vue.component() usage changed in Vue 3",
        "suggestion": "Use app.component() on the application instance"
    },

    # Vue.directive global registration
    "vue_directive_global": {
        "pattern": r"Vue\.directive\s*\(",
        "category": "global-api",
        "severity": "breaking",
        "description": "Global Vue.directive() usage changed in Vue 3",
        "suggestion": "Use app.directive() on the application instance"
    },

    # Vue.mixin global
    "vue_mixin_global": {
        "pattern": r"Vue\.mixin\s*\(",
        "category": "global-api",
        "severity": "breaking",
        "description": "Global Vue.mixin() usage changed in Vue 3",
        "suggestion": "Use app.mixin() or preferably Composition API composables"
    },

    # Vue.use
    "vue_use": {
        "pattern": r"Vue\.use\s*\(",
        "category": "global-api",
        "severity": "breaking",
        "description": "Vue.use() changed in Vue 3",
        "suggestion": "Use app.use() on the application instance"
    },

    # new Vue()
    "new_vue": {
        "pattern": r"new\s+Vue\s*\(",
        "category": "global-api",
        "severity": "breaking",
        "description": "new Vue() is replaced with createApp() in Vue 3",
        "suggestion": "Use createApp(App).mount('#app')"
    },

    # Vue.config
    "vue_config": {
        "pattern": r"Vue\.config\.",
        "category": "global-api",
        "severity": "warning",
        "description": "Vue.config is now app.config in Vue 3",
        "suggestion": "Use app.config on the application instance"
    },

    # Vue.prototype
    "vue_prototype": {
        "pattern": r"Vue\.prototype\.",
        "category": "global-api",
        "severity": "breaking",
        "description": "Vue.prototype is removed in Vue 3",
        "suggestion": "Use app.config.globalProperties"
    },

    # Functional component syntax
    "functional_component": {
        "pattern": r"functional\s*:\s*true",
        "category": "component",
        "severity": "breaking",
        "description": "Functional component syntax changed in Vue 3",
        "suggestion": "Use plain functions or remove functional option"
    },

    # Transition class names
    "v-enter": {
        "pattern": r"\.v-enter\b(?!-)",
        "category": "transition",
        "severity": "breaking",
        "description": "v-enter class renamed to v-enter-from in Vue 3",
        "suggestion": "Rename to v-enter-from"
    },
    "v-leave": {
        "pattern": r"\.v-leave\b(?!-)",
        "category": "transition",
        "severity": "breaking",
        "description": "v-leave class renamed to v-leave-from in Vue 3",
        "suggestion": "Rename to v-leave-from"
    },

    # Vuex patterns
    "vuex_store": {
        "pattern": r"new\s+Vuex\.Store\s*\(",
        "category": "vuex",
        "severity": "warning",
        "description": "Vuex store creation syntax differs; consider migrating to Pinia",
        "suggestion": "Migrate to Pinia using defineStore()"
    },
    "mapState": {
        "pattern": r"\bmapState\s*\(",
        "category": "vuex",
        "severity": "info",
        "description": "mapState helper - consider migrating to Pinia",
        "suggestion": "With Pinia, use storeToRefs() for reactive destructuring"
    },

    # Vue Router patterns
    "vue_router_new": {
        "pattern": r"new\s+VueRouter\s*\(",
        "category": "router",
        "severity": "breaking",
        "description": "new VueRouter() changed to createRouter() in Vue Router 4",
        "suggestion": "Use createRouter({ history: createWebHistory(), routes })"
    },
    "router_mode": {
        "pattern": r"mode\s*:\s*['\"](?:history|hash)['\"]",
        "category": "router",
        "severity": "breaking",
        "description": "Router mode option replaced with history option in Vue Router 4",
        "suggestion": "Use history: createWebHistory() or createWebHashHistory()"
    },

    # Options API patterns (info for conversion)
    "options_data_function": {
        "pattern": r"\bdata\s*\(\s*\)\s*\{",
        "category": "options-api",
        "severity": "info",
        "description": "Options API data() - can be converted to Composition API",
        "suggestion": "Consider using ref() or reactive() in setup()"
    },
    "options_computed": {
        "pattern": r"\bcomputed\s*:\s*\{",
        "category": "options-api",
        "severity": "info",
        "description": "Options API computed - can be converted to Composition API",
        "suggestion": "Consider using computed() in setup()"
    },
    "options_watch": {
        "pattern": r"\bwatch\s*:\s*\{",
        "category": "options-api",
        "severity": "info",
        "description": "Options API watch - can be converted to Composition API",
        "suggestion": "Consider using watch() or watchEffect() in setup()"
    },
    "options_methods": {
        "pattern": r"\bmethods\s*:\s*\{",
        "category": "options-api",
        "severity": "info",
        "description": "Options API methods - can be converted to Composition API",
        "suggestion": "Consider defining functions directly in setup()"
    },
}


def analyze_file(filepath: str, content: str, report: AnalysisReport):
    """Analyze a single file for Vue 2 patterns that need migration."""
    lines = content.split('\n')

    for name, config in PATTERNS.items():
        pattern = re.compile(config["pattern"])
        for line_num, line in enumerate(lines, 1):
            if pattern.search(line):
                report.add_issue(MigrationIssue(
                    file=filepath,
                    line=line_num,
                    category=config["category"],
                    severity=config["severity"],
                    description=config["description"],
                    suggestion=config["suggestion"]
                ))


def scan_directory(path: str) -> AnalysisReport:
    """Scan directory for Vue/JS files and analyze them."""
    report = AnalysisReport()

    for root, dirs, files in os.walk(path):
        # Skip node_modules and common build directories
        dirs[:] = [d for d in dirs if d not in ['node_modules', 'dist', 'build', '.git', 'docs']]

        for file in files:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, path)
            report.total_files += 1

            if file.endswith('.vue'):
                report.vue_files += 1
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                analyze_file(rel_path, content, report)

            elif file.endswith(('.js', '.ts')):
                report.js_files += 1
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                analyze_file(rel_path, content, report)

    return report


def print_report(report: AnalysisReport, output_format: str = 'text'):
    """Print the analysis report."""
    if output_format == 'json':
        print(json.dumps(report.to_dict(), indent=2))
        return

    data = report.to_dict()
    summary = data["summary"]

    print("\n" + "=" * 60)
    print("  Vue 2 to Vue 3 Migration Analysis Report")
    print("=" * 60)

    print(f"\n📁 Files Scanned:")
    print(f"   Total: {summary['total_files']}")
    print(f"   Vue files: {summary['vue_files']}")
    print(f"   JS/TS files: {summary['js_files']}")

    print(f"\n📊 Issues Found:")
    print(f"   🔴 Breaking changes: {summary['breaking_changes']}")
    print(f"   🟡 Warnings: {summary['warnings']}")
    print(f"   🔵 Info: {summary['info']}")

    if report.issues:
        print("\n" + "-" * 60)
        print("  Detailed Issues")
        print("-" * 60)

        # Group by category
        by_category: Dict[str, List[MigrationIssue]] = {}
        for issue in report.issues:
            if issue.category not in by_category:
                by_category[issue.category] = []
            by_category[issue.category].append(issue)

        for category, issues in sorted(by_category.items()):
            print(f"\n📂 {category.upper()}")
            for issue in issues:
                severity_icon = {"breaking": "🔴", "warning": "🟡", "info": "🔵"}[issue.severity]
                print(f"   {severity_icon} {issue.file}:{issue.line}")
                print(f"      {issue.description}")
                print(f"      → {issue.suggestion}")

    print("\n" + "=" * 60)


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze-vue2.py <project-path> [--json]")
        print("\nAnalyzes a Vue 2 project and identifies migration issues for Vue 3.")
        sys.exit(1)

    path = sys.argv[1]
    output_format = 'json' if '--json' in sys.argv else 'text'

    if not os.path.exists(path):
        print(f"Error: Path '{path}' does not exist")
        sys.exit(1)

    report = scan_directory(path)
    print_report(report, output_format)


if __name__ == "__main__":
    main()
