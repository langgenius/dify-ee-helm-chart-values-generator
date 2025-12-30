"""
Trigger Worker Feature - Available from Chart version 3.7.0+

This feature adds the triggerWorker service configuration for workflow trigger functionality.
The triggerWorker is a dedicated Celery worker for handling workflow triggers.
"""

from .base import Feature, register_feature
from utils import print_section, print_info, print_success, prompt, prompt_yes_no
from i18n import get_translator


@register_feature(
    min_version="3.7.0",
    module="services",
    name="Trigger Worker Service",
    description="Configure triggerWorker service for workflow trigger processing"
)
class TriggerWorkerFeature(Feature):
    """
    Configure triggerWorker service (3.7.0+)

    This service is used for:
    - Processing workflow webhook triggers
    - Handling scheduled workflow executions
    - Managing trigger-based workflow invocations
    """

    def configure(self, generator) -> None:
        """Configure trigger worker service settings"""
        _t = get_translator()

        print_section(_t('trigger_worker_config'))
        print_info(_t('trigger_worker_desc'))

        # Ensure triggerWorker configuration exists
        if 'triggerWorker' not in generator.values:
            generator.values['triggerWorker'] = {}

        # Check if user wants to configure trigger worker
        if not prompt_yes_no(_t('config_trigger_worker'), default=False):
            print_info(_t('using_default_trigger_worker'))
            return

        # Configure replicas
        replicas_input = prompt(
            _t('trigger_worker_replicas'),
            default=str(generator.values.get('triggerWorker', {}).get('replicas', 1)),
            required=False
        )
        try:
            replicas = int(replicas_input)
            if replicas >= 1:
                generator.values['triggerWorker']['replicas'] = replicas
        except ValueError:
            pass

        # Configure celery worker amount
        celery_input = prompt(
            _t('trigger_worker_celery_amount'),
            default=str(generator.values.get('triggerWorker', {}).get('celeryWorkerAmount', 1)),
            required=False
        )
        try:
            celery_amount = int(celery_input)
            if celery_amount >= 1:
                generator.values['triggerWorker']['celeryWorkerAmount'] = celery_amount
        except ValueError:
            pass

        # Configure code execution limits
        print_info(_t('trigger_worker_code_limits_desc'))

        if prompt_yes_no(_t('config_trigger_worker_code_limits'), default=False):
            # Ensure code section exists
            if 'code' not in generator.values['triggerWorker']:
                generator.values['triggerWorker']['code'] = {}

            max_string = prompt(
                _t('max_string_array_length'),
                default=str(generator.values.get('triggerWorker', {}).get('code', {}).get('maxStringArrayLength', 500)),
                required=False
            )
            try:
                generator.values['triggerWorker']['code']['maxStringArrayLength'] = int(max_string)
            except ValueError:
                pass

            max_object = prompt(
                _t('max_object_array_length'),
                default=str(generator.values.get('triggerWorker', {}).get('code', {}).get('maxObjectArrayLength', 500)),
                required=False
            )
            try:
                generator.values['triggerWorker']['code']['maxObjectArrayLength'] = int(max_object)
            except ValueError:
                pass

            max_number = prompt(
                _t('max_number_array_length'),
                default=str(generator.values.get('triggerWorker', {}).get('code', {}).get('maxNumberArrayLength', 500)),
                required=False
            )
            try:
                generator.values['triggerWorker']['code']['maxNumberArrayLength'] = int(max_number)
            except ValueError:
                pass

        print_success(_t('trigger_worker_configured'))
