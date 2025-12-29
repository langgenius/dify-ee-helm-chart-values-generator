"""
Version-specific features module

This module provides a framework for managing version-specific configuration features.
Each feature declares its applicable version range and is automatically loaded when
the current chart version matches.

Architecture:
- FeatureRegistry: Central registry for all version-specific features
- Feature: Base class for defining version-specific configuration logic
- Each feature module (e.g., trigger_domain.py) registers features with version constraints

Usage:
1. Create a new feature file in modules/features/
2. Inherit from Feature base class
3. Use @register_feature decorator to register with version constraints
4. Features are automatically discovered and applied during configuration

Example:
    from modules.features import Feature, register_feature

    @register_feature(min_version="3.7.0", module="global")
    class TriggerDomainFeature(Feature):
        def configure(self, generator):
            # Configuration logic here
            pass
"""

from .base import Feature, FeatureRegistry, register_feature, apply_features

__all__ = [
    'Feature',
    'FeatureRegistry',
    'register_feature',
    'apply_features',
]

# Auto-discover and import all feature modules
def _discover_features():
    """Automatically discover and import all feature modules"""
    import os
    import importlib
    from pathlib import Path

    features_dir = Path(__file__).parent
    for file in features_dir.glob("*.py"):
        if file.name.startswith("_") or file.name == "base.py":
            continue
        module_name = file.stem
        try:
            importlib.import_module(f".{module_name}", package=__name__)
        except ImportError as e:
            print(f"Warning: Failed to import feature module {module_name}: {e}")

# Discover features on module load
_discover_features()

