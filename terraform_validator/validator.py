import re
import sys
import logging


class ResourceContainer:
    """
    A readonly object that mimics the usage of a dictionary.
    Plus, one can use regex as key and container will return all values in an array whose key matches the regex.
    """

    def __init__(self, resource_dict):
        self.resource_dict = resource_dict

    def __getitem__(self, regex_key):
        """
        Mimic the [] access of a dictionary
        :param regex_key:
        :return: A single value if key string exists. Otherwise, an array of values if matched by regex.
        """
        if regex_key in self.resource_dict:
            return self.resource_dict[regex_key]
        else:
            pattern = re.compile(regex_key)
            matched_vals = [self.resource_dict[key] for key in self.resource_dict if pattern.match(key)]
            if len(matched_vals) > 0:
                return matched_vals
            else:
                raise KeyError(regex_key)  # if cannot match any key, throw KeyError


class TerraformValidator:
    """
    Class that validates terraform plan by rules.
    """

    def __init__(self, rule_configs):
        self.rule_configs = rule_configs

    def _get_resource_type(self, resource_name):
        """
        Extract the name of resource type based on resource name
        :param resource_name: resource name, e.g. aws_db_instance.test_service_db
        :return: string of resource type name, e.g. aws_db_instance
        """
        return resource_name.split('.')[0]

    def validate(self, tfplan):
        """
        Loop through each resource in terraform plan and validate rules agains them.
        :param tfplan: terraform plan dictionary
        :return: Array of tuples of validation error messages. for each tuple,
        first element is the a string of resource name, second element is a string explains the reason.
        """
        errors = []
        for resource_name in tfplan:
            for resource_config in self.rule_configs:
                if resource_config['resource'] == self._get_resource_type(resource_name):
                    for rule in resource_config['rules']:
                        if not self.validate_rule(rule, tfplan[resource_name]):
                            errors.append((resource_name, rule['name']))
        return errors

    def validate_rule(self, rule, resource):
        """
        Validate a single rule on the values of a resource by eval the boolean value of rule's expression.
        :param rule: rule dictionary
        :param resource: resource values dictionary
        :return: True if valid, otherwise False
        """
        try:
            if 'destroy' in resource and resource['destroy']:
                return True  # skip validation if resource is being destroyed
            R = ResourceContainer(resource)  # R is the identifier used in the rule expression
            return eval(rule["expr"])
        except Exception as e:
            '''exceptions are suppressed here to let the validation continue. So that the user will
            receive al complete report and be able to fix all errors at once.'''
            logging.exception('[EXCEPTION] Exception occurred during rule expression evaluation')
            return False
