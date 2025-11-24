"""Networking configuration module"""

from utils import (
    print_header, print_section, print_info, print_success, print_warning, print_error,
    prompt, prompt_choice, prompt_yes_no, generate_secret
)
from version_manager import VersionManager
from i18n import get_translator

_t = get_translator()


def configure_networking(generator):
    """Configure networking"""
    print_header(_t('module_networking'))

    # TLS configuration - placed in networking module, linked with Ingress
    print_section(_t('tls_config'))
    print_info(_t('tls_config_affects'))
    print_warning(_t('tls_config_must_match'))

    use_tls = prompt_yes_no(_t('enable_tls_internal'), default=False)
    generator.values['global']['useTLS'] = use_tls

    if use_tls:
        print_info(_t('tls_enabled_ingress_note'))

    # Ingress configuration
    print_section(_t('ingress_config'))
    # Enterprise edition defaults to enabling Ingress
    generator.values['ingress']['enabled'] = True
    print_info(_t('ingress_auto_enabled'))

    # Ingress Class Selection
    print_info("")
    print_info(_t('select_ingress_controller_type'))
    ingress_class_choice = prompt_choice(
        _t('ingress_class_name'),
        ["nginx", "alb", "traefik", "istio", _t('other')],
        default="nginx"
    )

    if ingress_class_choice == "nginx":
        generator.values['ingress']['className'] = "nginx"
        print_info("")
        print_warning(_t('ensure_nginx_installed'))
        print_info(_t('nginx_install_method'))
    elif ingress_class_choice == "alb":
        generator.values['ingress']['className'] = "alb"
        print_info("")
        print_warning(_t('ensure_alb_installed'))
        print_info(_t('alb_install_method'))
    elif ingress_class_choice == "traefik":
        generator.values['ingress']['className'] = "traefik"
        print_info("")
        print_warning(_t('ensure_traefik_installed'))
    elif ingress_class_choice == "istio":
        generator.values['ingress']['className'] = "istio"
        print_info("")
        print_warning(_t('ensure_istio_installed'))
    else:
        # Other option, manual input
        generator.values['ingress']['className'] = prompt(
            _t('enter_ingress_class_name'),
            default="",
            required=False
        )

    # Ingress TLS Configuration - Linked with global TLS
    if use_tls:
        print_info(_t('global_tls_enabled_ingress_note'))
        ingress_tls = prompt_yes_no(_t('config_tls_in_ingress'), default=True)
    else:
        ingress_tls = prompt_yes_no(_t('config_tls_in_ingress'), default=False)

    if ingress_tls:
        print_info(_t('tls_cert_config'))
        print_info(_t('cert_manager_option'))
        print_info(_t('manual_tls_secret_option'))

        # TLS configuration example
        tls_hosts = prompt(
            _t('tls_hosts_list'),
            default="",
            required=False
        )

        if tls_hosts:
            hosts_list = [h.strip() for h in tls_hosts.split(',') if h.strip()]
            if hosts_list:
                # Create TLS configuration
                if 'tls' not in generator.values['ingress'] or not isinstance(generator.values['ingress']['tls'], list):
                    generator.values['ingress']['tls'] = []

                generator.values['ingress']['tls'].append({
                    'hosts': hosts_list,
                    'secretName': prompt(
                        _t('tls_secret_name'),
                        default=f"{hosts_list[0]}-tls",
                        required=False
                    ) or f"{hosts_list[0]}-tls"
                })

        # Add cert-manager annotation example
        if prompt_yes_no(_t('use_cert_manager'), default=False):
            if 'annotations' not in generator.values['ingress']:
                generator.values['ingress']['annotations'] = {}

            cluster_issuer = prompt(
                _t('cluster_issuer_name'),
                default="",
                required=False
            )
            if cluster_issuer:
                generator.values['ingress']['annotations']['cert-manager.io/cluster-issuer'] = cluster_issuer
                print_success(f"{_t('cert_manager_configured')}: {cluster_issuer}")

    # Check TLS consistency
    if use_tls and not ingress_tls:
        print_warning(_t('tls_inconsistency_warning'))
        if prompt_yes_no(_t('enable_ingress_tls_now'), default=True):
            ingress_tls = True
            # Reconfigure TLS
            tls_hosts = prompt(
                _t('tls_hosts_list_comma'),
                default="",
                required=False
            )
            if tls_hosts:
                hosts_list = [h.strip() for h in tls_hosts.split(',') if h.strip()]
                if hosts_list:
                    if 'tls' not in generator.values['ingress'] or not isinstance(generator.values['ingress']['tls'], list):
                        generator.values['ingress']['tls'] = []
                    generator.values['ingress']['tls'].append({
                        'hosts': hosts_list,
                        'secretName': prompt(
                            _t('tls_secret_name'),
                            default=f"{hosts_list[0]}-tls",
                            required=False
                        ) or f"{hosts_list[0]}-tls"
                    })

    if not use_tls and ingress_tls:
        print_warning(_t('ingress_tls_enabled_global_not_warning'))
        if prompt_yes_no(_t('enable_global_tls'), default=True):
            generator.values['global']['useTLS'] = True
            use_tls = True

    # useIpAsHost configuration - Enterprise edition doesn't support, fixed to False
    generator.values['ingress']['useIpAsHost'] = False

