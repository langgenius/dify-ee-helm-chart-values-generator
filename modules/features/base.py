"""
Feature base classes and registry for version-specific configurations

This module provides the core infrastructure for managing version-specific features:
- Semantic version comparison
- Feature registration with version constraints
- Automatic feature discovery and application
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Callable, Any, Type
from functools import wraps
import re


def parse_version(version_str: str) -> tuple:
    """
    Parse version string into comparable tuple

    Handles versions like:
    - "3.7.0" -> (3, 7, 0, "", 0)
    - "3.6.0-beta.1" -> (3, 6, 0, "beta", 1)
    - "3.6.0-alpha.2" -> (3, 6, 0, "alpha", 2)
    - "3.6.0-rc.1" -> (3, 6, 0, "rc", 1)

    Pre-release versions are considered less than release versions:
    3.6.0-alpha.1 < 3.6.0-beta.1 < 3.6.0-rc.1 < 3.6.0
    """
    if not version_str:
        return (0, 0, 0, "", 0)

    # Split main version and pre-release
    parts = version_str.split("-", 1)
    main_version = parts[0]
    pre_release = parts[1] if len(parts) > 1 else ""

    # Parse main version (major.minor.patch)
    version_parts = main_version.split(".")
    major = int(version_parts[0]) if len(version_parts) > 0 else 0
    minor = int(version_parts[1]) if len(version_parts) > 1 else 0
    patch = int(version_parts[2]) if len(version_parts) > 2 else 0

    # Parse pre-release (e.g., "beta.1", "alpha.2", "rc.1")
    pre_type = ""
    pre_num = 0
    if pre_release:
        pre_match = re.match(r"([a-zA-Z]+)\.?(\d+)?", pre_release)
        if pre_match:
            pre_type = pre_match.group(1).lower()
            pre_num = int(pre_match.group(2)) if pre_match.group(2) else 0

    # Pre-release priority: "" (release) > "rc" > "beta" > "alpha"
    # Use higher number for release (empty string = highest priority)
    pre_priority = {
        "": 999,  # Release version has highest priority
        "rc": 3,
        "beta": 2,
        "alpha": 1,
    }

    return (major, minor, patch, pre_priority.get(pre_type, 0), pre_num)


def compare_versions(v1: str, v2: str) -> int:
    """
    Compare two version strings

    Returns:
        -1 if v1 < v2
         0 if v1 == v2
         1 if v1 > v2
    """
    parsed_v1 = parse_version(v1)
    parsed_v2 = parse_version(v2)

    if parsed_v1 < parsed_v2:
        return -1
    elif parsed_v1 > parsed_v2:
        return 1
    return 0


def version_satisfies(version: str, min_version: Optional[str] = None, max_version: Optional[str] = None) -> bool:
    """
    Check if version satisfies the given constraints

    Args:
        version: The version to check
        min_version: Minimum version (inclusive), None means no minimum
        max_version: Maximum version (inclusive), None means no maximum

    Returns:
        True if version satisfies constraints
    """
    if min_version and compare_versions(version, min_version) < 0:
        return False
    if max_version and compare_versions(version, max_version) > 0:
        return False
    return True


class Feature(ABC):
    """
    Base class for version-specific features

    Each feature must implement:
    - name: Human-readable feature name
    - configure(): Configuration logic to apply
    """

    # Feature metadata (set by decorator or subclass)
    name: str = ""
    description: str = ""
    min_version: Optional[str] = None
    max_version: Optional[str] = None
    module: str = ""  # Which module this feature belongs to (e.g., "global", "networking")

    @abstractmethod
    def configure(self, generator) -> None:
        """
        Apply feature configuration

        Args:
            generator: ValuesGenerator instance
        """
        pass

    def is_applicable(self, chart_version: str) -> bool:
        """
        Check if this feature applies to the given chart version

        Args:
            chart_version: Helm Chart version string

        Returns:
            True if feature should be applied
        """
        return version_satisfies(chart_version, self.min_version, self.max_version)


class FeatureRegistry:
    """
    Central registry for all version-specific features

    Features are registered with version constraints and module associations.
    During configuration, applicable features are automatically applied.
    """

    _features: Dict[str, List[Type[Feature]]] = {}

    @classmethod
    def register(cls, feature_class: Type[Feature], module: str = "") -> None:
        """
        Register a feature class

        Args:
            feature_class: Feature class to register
            module: Module this feature belongs to
        """
        if module not in cls._features:
            cls._features[module] = []
        cls._features[module].append(feature_class)

    @classmethod
    def get_features_for_module(cls, module: str, chart_version: str) -> List[Feature]:
        """
        Get all applicable features for a module and version

        Args:
            module: Module name (e.g., "global", "networking")
            chart_version: Helm Chart version

        Returns:
            List of Feature instances that apply to this version
        """
        features = []
        for feature_class in cls._features.get(module, []):
            feature = feature_class()
            if feature.is_applicable(chart_version):
                features.append(feature)
        return features

    @classmethod
    def get_all_features(cls, chart_version: str) -> Dict[str, List[Feature]]:
        """
        Get all applicable features grouped by module

        Args:
            chart_version: Helm Chart version

        Returns:
            Dict mapping module names to lists of applicable features
        """
        result = {}
        for module, feature_classes in cls._features.items():
            applicable = []
            for feature_class in feature_classes:
                feature = feature_class()
                if feature.is_applicable(chart_version):
                    applicable.append(feature)
            if applicable:
                result[module] = applicable
        return result

    @classmethod
    def clear(cls) -> None:
        """Clear all registered features (useful for testing)"""
        cls._features.clear()


def register_feature(
    min_version: Optional[str] = None,
    max_version: Optional[str] = None,
    module: str = "global",
    name: str = "",
    description: str = ""
) -> Callable[[Type[Feature]], Type[Feature]]:
    """
    Decorator to register a feature with version constraints

    Args:
        min_version: Minimum chart version (inclusive)
        max_version: Maximum chart version (inclusive)
        module: Module this feature belongs to
        name: Human-readable feature name
        description: Feature description

    Example:
        @register_feature(min_version="3.7.0", module="global")
        class TriggerDomainFeature(Feature):
            def configure(self, generator):
                pass
    """
    def decorator(cls: Type[Feature]) -> Type[Feature]:
        cls.min_version = min_version
        cls.max_version = max_version
        cls.module = module
        if name:
            cls.name = name
        if description:
            cls.description = description

        FeatureRegistry.register(cls, module)
        return cls

    return decorator


def apply_features(generator, module: str) -> None:
    """
    Apply all applicable features for a module

    This function should be called at the end of each module's configure function
    to apply version-specific features.

    Args:
        generator: ValuesGenerator instance
        module: Module name (e.g., "global", "networking")
    """
    from utils import print_info, print_success
    from i18n import get_translator

    _t = get_translator()

    chart_version = generator.chart_version
    if not chart_version:
        return

    features = FeatureRegistry.get_features_for_module(module, chart_version)
    for feature in features:
        feature_name = feature.name or feature.__class__.__name__
        print_info(f"  → {_t('applying_feature')}: {feature_name} (>= {feature.min_version})")
        feature.configure(generator)
        print_success(f"    ✓ {feature_name}")

