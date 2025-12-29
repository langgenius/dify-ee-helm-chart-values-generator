"""
Plugin Metric Feature - Available from Chart version 3.7.0+

This feature adds plugin_manager.metric configuration for plugin resource monitoring.
Supports multiple metric sources: disabled, cadvisor, or prometheus.
"""

from .base import Feature, register_feature
from utils import print_section, print_info, print_success, print_warning, prompt, prompt_choice, prompt_yes_no
from i18n import get_translator


@register_feature(
    min_version="3.7.0",
    module="plugins",
    name="Plugin Metrics",
    description="Configure plugin resource monitoring (CPU, memory, network I/O)"
)
class PluginMetricFeature(Feature):
    """
    Configure plugin_manager.metric settings (3.7.0+)

    This feature enables monitoring of plugin resources:
    - CPU usage
    - Memory usage
    - Network I/O

    Metric sources:
    - disabled: No metrics collected
    - cadvisor: Metrics from cadvisor (requires cluster roles)
    - prometheus: Query from external Prometheus (recommended)
    """

    def configure(self, generator) -> None:
        """Configure plugin metrics settings"""
        _t = get_translator()

        print_section(_t('plugin_metric_config'))
        print_info(_t('plugin_metric_desc'))

        # Ensure plugin_manager configuration exists
        if 'plugin_manager' not in generator.values:
            generator.values['plugin_manager'] = {}

        # Check if user wants to configure plugin metrics
        if not prompt_yes_no(_t('config_plugin_metric'), default=False):
            print_info(_t('using_default_plugin_metric'))
            return

        # Select metric source
        print_info("")
        print_info(_t('plugin_metric_source_options'))
        print_info(f"  • disabled - {_t('plugin_metric_disabled_desc')}")
        print_info(f"  • cadvisor - {_t('plugin_metric_cadvisor_desc')}")
        print_info(f"  • prometheus - {_t('plugin_metric_prometheus_desc')}")

        metric_source = prompt_choice(
            _t('plugin_metric_source'),
            ["disabled", "cadvisor", "prometheus"],
            default=generator.values.get('plugin_manager', {}).get('metric', {}).get('source', 'disabled')
        )

        # Ensure metric section exists
        if 'metric' not in generator.values['plugin_manager']:
            generator.values['plugin_manager']['metric'] = {}

        generator.values['plugin_manager']['metric']['source'] = metric_source

        if metric_source == "cadvisor":
            print_warning(_t('cadvisor_cluster_role_warning'))

            # Configure scrape settings
            if prompt_yes_no(_t('config_cadvisor_scrape'), default=False):
                if 'scrape' not in generator.values['plugin_manager']['metric']:
                    generator.values['plugin_manager']['metric']['scrape'] = {}

                scrape_interval = prompt(
                    _t('scrape_interval'),
                    default=generator.values['plugin_manager']['metric'].get('scrape', {}).get('scrapeInterval', '20s'),
                    required=False
                )
                generator.values['plugin_manager']['metric']['scrape']['scrapeInterval'] = scrape_interval

                scrape_timeout = prompt(
                    _t('scrape_timeout'),
                    default=generator.values['plugin_manager']['metric'].get('scrape', {}).get('scrapeTimeout', '10s'),
                    required=False
                )
                generator.values['plugin_manager']['metric']['scrape']['scrapeTimeout'] = scrape_timeout

                retain_period = prompt(
                    _t('retain_period'),
                    default=generator.values['plugin_manager']['metric'].get('scrape', {}).get('retainPeriod', '604800s'),
                    required=False
                )
                generator.values['plugin_manager']['metric']['scrape']['retainPeriod'] = retain_period

        elif metric_source == "prometheus":
            print_info(_t('prometheus_external_required'))
            print_info(_t('prometheus_config_in_infrastructure'))

        print_success(_t('plugin_metric_configured'))
