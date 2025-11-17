from dataclasses import dataclass
from typing import List, Dict
import json
import os


@dataclass
class ValidationResult:
    component: str
    status: str  # 'pass', 'warning', 'fail'
    message: str
    fix_applied: bool = False


@dataclass
class DeploymentConfig:
    vercel_json_valid: bool = False
    procfile_exists: bool = False
    vercelignore_exists: bool = False
    runtime_txt_exists: bool = False
    dependencies_valid: bool = False
    streamlit_config_valid: bool = False
    overall_ready: bool = False


class DeploymentConfigValidator:
    """Lightweight validator for deployment configuration expected by tests.

    This file is intentionally simple: it checks the presence/sanity of
    files like `vercel.json`, `Procfile`, `.vercelignore` and `runtime.txt`.
    It provides the methods the tests import and exercise.
    """

    def __init__(self, root: str | None = None):
        self.root = root or os.getcwd()

    def _read_json(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def validate_vercel_json(self) -> ValidationResult:
        path = os.path.join(self.root, 'vercel.json')
        if not os.path.exists(path):
            return ValidationResult('vercel.json', 'warning', 'vercel.json not found')

        data = self._read_json(path)
        if data is None:
            return ValidationResult('vercel.json', 'fail', 'vercel.json is invalid JSON')

        # Basic sanity: should be a dict
        if isinstance(data, dict):
            return ValidationResult('vercel.json', 'pass', 'vercel.json looks valid')
        return ValidationResult('vercel.json', 'fail', 'vercel.json has unexpected structure')

    def validate_procfile(self) -> ValidationResult:
        path = os.path.join(self.root, 'Procfile')
        if os.path.exists(path):
            return ValidationResult('Procfile', 'pass', 'Procfile exists')
        return ValidationResult('Procfile', 'warning', 'Procfile not found')

    def validate_vercelignore(self) -> ValidationResult:
        path = os.path.join(self.root, '.vercelignore')
        if os.path.exists(path):
            return ValidationResult('.vercelignore', 'pass', '.vercelignore exists')
        return ValidationResult('.vercelignore', 'warning', '.vercelignore not found')

    def validate_runtime_txt(self) -> ValidationResult:
        path = os.path.join(self.root, 'runtime.txt')
        if os.path.exists(path):
            return ValidationResult('runtime.txt', 'pass', 'runtime.txt exists')
        return ValidationResult('runtime.txt', 'warning', 'runtime.txt not found')

    def validate_dependencies(self) -> ValidationResult:
        req = os.path.join(self.root, 'requirements.txt')
        if not os.path.exists(req):
            return ValidationResult('dependencies', 'warning', 'requirements.txt not found')

        try:
            with open(req, 'r', encoding='utf-8') as f:
                lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
            if lines:
                return ValidationResult('dependencies', 'pass', 'requirements.txt looks present')
            return ValidationResult('dependencies', 'warning', 'requirements.txt empty')
        except Exception:
            return ValidationResult('dependencies', 'fail', 'Could not read requirements.txt')

    def validate_streamlit_config(self) -> ValidationResult:
        # Basic heuristic: check if app.py exists and imports streamlit
        app_py = os.path.join(self.root, 'app.py')
        if not os.path.exists(app_py):
            return ValidationResult('streamlit', 'warning', 'app.py not found')

        try:
            with open(app_py, 'r', encoding='utf-8') as f:
                src = f.read()
            if 'import streamlit' in src or 'streamlit as st' in src:
                return ValidationResult('streamlit', 'pass', 'Streamlit app detected')
            return ValidationResult('streamlit', 'warning', 'app.py does not appear to import streamlit')
        except Exception:
            return ValidationResult('streamlit', 'fail', 'Could not read app.py')

    def validate_all_files(self) -> List[ValidationResult]:
        results = []
        results.append(self.validate_vercel_json())
        results.append(self.validate_procfile())
        results.append(self.validate_vercelignore())
        results.append(self.validate_runtime_txt())
        results.append(self.validate_dependencies())
        results.append(self.validate_streamlit_config())
        return results

    def get_deployment_config_status(self) -> DeploymentConfig:
        results = self.validate_all_files()
        cfg = DeploymentConfig()
        for r in results:
            if r.component == 'vercel.json':
                cfg.vercel_json_valid = r.status == 'pass'
            if r.component == 'Procfile':
                cfg.procfile_exists = r.status == 'pass'
            if r.component == '.vercelignore':
                cfg.vercelignore_exists = r.status == 'pass'
            if r.component == 'runtime.txt':
                cfg.runtime_txt_exists = r.status == 'pass'
            if r.component == 'dependencies':
                cfg.dependencies_valid = r.status == 'pass'
            if r.component == 'streamlit':
                cfg.streamlit_config_valid = r.status == 'pass'

        cfg.overall_ready = all([
            cfg.vercel_json_valid,
            cfg.procfile_exists,
            cfg.runtime_txt_exists,
            cfg.dependencies_valid,
            cfg.streamlit_config_valid,
        ])
        return cfg

    def generate_validation_report(self) -> Dict:
        results = self.validate_all_files()
        summary = {'total_checks': len(results), 'passed': 0, 'warnings': 0, 'failed': 0}
        recommendations = []
        for r in results:
            if r.status == 'pass':
                summary['passed'] += 1
            elif r.status == 'warning':
                summary['warnings'] += 1
                recommendations.append(f"Check {r.component}: {r.message}")
            else:
                summary['failed'] += 1
                recommendations.append(f"Fix {r.component}: {r.message}")

        overall = 'ready' if summary['failed'] == 0 else 'not_ready'
        return {
            'overall_status': overall,
            'summary': summary,
            'recommendations': recommendations,
        }


# Backwards compatibility convenience names expected by some tests
ValidationResult = ValidationResult
DeploymentConfig = DeploymentConfig
DeploymentConfigValidator = DeploymentConfigValidator
