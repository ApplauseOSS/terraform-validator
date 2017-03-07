import json
import os
import subprocess
import sys


def read_rules_file(rules_file_path):
    """
    :param rules_file_path: rule json file path
    :return: rules array loaded from json file
    """
    with open(rules_file_path) as rules_file:
        return json.load(rules_file)


def read_plan_file(plan_file_path):
    """
    Converts .tfplan to json and load json to a plan dictionary.
    Automatically choose the proper tfjson binary based on operating system.
    :param plan_file_path: .tfplan file path
    :return: plan dictionary
    """
    if sys.platform.startswith('linux'):
        tfjson_bin = 'tfjson'
    elif sys.platform == 'darwin':
        tfjson_bin = 'tfjson-mac'
    else:
        raise Exception('Operating system not supported.')
    proc = subprocess.Popen(
        os.path.dirname(os.path.realpath(__file__)) + '/dependencies/%s %s'
        % (tfjson_bin, plan_file_path, ), shell=True, stdout=subprocess.PIPE)
    return json.load(proc.stdout)
