"""
External Prometheus Feature - Available from Chart version 3.7.0+

This feature adds externalPrometheus configuration for plugin metrics monitoring.
When enabled, plugin_manager can query metrics from an external Prometheus server.
"""

from .base import Feature, register_feature
from utils import print_section, print_info, print_success, print_warning, prompt, prompt_yes_no
from i18n import get_translator


@register_feature(
    min_version="3.7.0",
    module="infrastructure",
    name="External Prometheus",
    description="Configure external Prometheus for plugin metrics monitoring"
)
class ExternalPrometheusFeature(Feature):
    """
    Configure externalPrometheus settings (3.7.0+)

    This feature provides an external Prometheus endpoint for plugin metrics:
    - Required when plugin_manager.metric.source = "prometheus"
    - Avoids the need for cluster roles required by cadvisor
    - Supports authentication (username/password)

    Required metrics:
    - container_cpu_usage_seconds_total
    - container_memory_working_set_bytes
    - container_network_receive_bytes_total
    - container_network_transmit_bytes_total
    """

    def configure(self, generator) -> None:
        """Configure external Prometheus settings"""
        _t = get_translator()

        print_section(_t('external_prometheus_config'))
        print_info(_t('external_prometheus_desc'))

        # Check if user wants to enable external Prometheus
        enable_prometheus = prompt_yes_no(
            _t('enable_external_prometheus'),
            default=generator.values.get('externalPrometheus', {}).get('enabled', False)
        )

        # Ensure externalPrometheus configuration exists
        if 'externalPrometheus' not in generator.values:
            generator.values['externalPrometheus'] = {}

        generator.values['externalPrometheus']['enabled'] = enable_prometheus

        if not enable_prometheus:
            print_info(_t('external_prometheus_disabled'))
            return

        # Configure Prometheus endpoint
        print_info(_t('external_prometheus_endpoint_desc'))

        endpoint = prompt(
            _t('prometheus_endpoint'),
            default=generator.values.get('externalPrometheus', {}).get('endpoint', 'http://prometheus:9090'),
            required=True
        )
        generator.values['externalPrometheus']['endpoint'] = endpoint

        # Configure timeout
        timeout = prompt(
            _t('prometheus_timeout'),
            default=generator.values.get('externalPrometheus', {}).get('timeout', '10s'),
            required=False
        )
        generator.values['externalPrometheus']['timeout'] = timeout

        # Configure authentication
        if prompt_yes_no(_t('prometheus_auth_required'), default=False):
            username = prompt(
                _t('prometheus_username'),
                default=generator.values.get('externalPrometheus', {}).get('username', ''),
                required=False
            )
            generator.values['externalPrometheus']['username'] = username

            password = prompt(
                _t('prometheus_password'),
                default='',
                required=False
            )
            if password:
                generator.values['externalPrometheus']['password'] = password

        # Configure insecure (skip TLS verification)
        insecure = prompt_yes_no(
            _t('prometheus_insecure'),
            default=generator.values.get('externalPrometheus', {}).get('insecure', True)
        )
        generator.values['externalPrometheus']['insecure'] = insecure

        if insecure:
            print_warning(_t('prometheus_insecure_warning'))

        print_success(_t('external_prometheus_configured'))
