import os
import re
import argparse
import subprocess
import shutil
import getpass

IDE_SUPPORT_LIST = [
        {'id': '1', 'key': 'clion', 'name': 'CLion'},
        {'id': '2', 'key': 'datagrip', 'name': 'DataGrip'},
        {'id': '3', 'key': 'idea', 'name': 'IntelliJIdea'},
        {'id': '4', 'key': 'goland', 'name': 'GoLand'},
        {'id': '5', 'key': 'phpstorm', 'name': 'PhpStorm'},
        ]

def print_ide_support_list():
    for item in IDE_SUPPORT_LIST:
        print(item.get('id') + ': ' + item.get('name'))

def find_ide(needle, key):
    ide = None
    for item in IDE_SUPPORT_LIST:
        if needle == item.get(key):
            ide = item
            break
    return ide

def find_versions(path, ide_name):
    versions = []
    for directory in os.listdir(path):
        if re.match('^{}*'.format(ide_name), directory):
            versions.append(directory)
    return versions

def find_current_version(path, ide_name):
    result = ''
    versions = find_versions(path, ide_name)
    if (len(versions) > 0):
        versions.sort()
        result = versions[-1]
    return result

def remove_files(dir_path, pattern):
    for f in os.listdir(dir_path):
        if re.search(pattern, f):
            os.remove(os.path.join(dir_path, f))

def remove_lines(file_path, pattern):
    updateLines = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if re.search(pattern, line):
                continue
            updateLines.append(line)

    if len(updateLines) > 0:
        with open(file_path, 'w') as file:
            file.writelines(updateLines)

def main():
    parser = argparse.ArgumentParser(description='Reset IDE')
    parser.add_argument(
            '-i', '--ide', type=str, required=False,
            help='IDE key, example: phpstorm')
    args = parser.parse_args()
    ide_key = args.ide

    ide_chosen = None
    if (not ide_key):
        print_ide_support_list()
        print('Choose IDE. Type number and press <Enter> (empty cancels):')
        ide_id = str(input())
        ide_chosen = find_ide(ide_id, 'id')
    else:
        ide_chosen = find_ide(ide_key, 'key')

    if (not ide_chosen):
        print('Not found support IDE')
        exit()

    username = getpass.getuser()
    home_path = '/home/{}'.format(username)
    if (not os.path.exists(home_path)):
        print('Not found user home path: {}'.format(home_path))
        exit()

    config_path = '{}/.config/JetBrains'.format(home_path)
    if (not os.path.exists(config_path)):
        print('Not found config IDE path: {}. This script works with JetBrains IDEs are older than 2020'.format(config_path))
        exit()

    ide_version = find_current_version(config_path, ide_chosen.get('name'))
    if (not ide_version):
        print('Not found current IDE version')
        exit()

    config_ide_path = '{}/{}'.format(config_path, ide_version)

    try:
        evaluation_folder = '{}/eval/'.format(config_ide_path)
        if (os.path.exists(evaluation_folder)):
            remove_files(evaluation_folder, '([a-zA-Z0-9]+)\.evaluation.key')
    except Exception as e:
        print('Not remove evaluation keys in folder: {}, error: {}'.format(evaluation_folder, str(e)))
        exit()

    try:
        other_xml = '{}/options/other.xml'.format(config_ide_path)
        if (os.path.exists(other_xml)):
            remove_lines(other_xml, 'evlsprt')
    except Exception as e:
        print('Not remove lines in {}, error: {}'.format(other_xml, str(e)))
        exit()

    ide_java_conf = '{}/.java/.userPrefs/jetbrains/{}/'.format(home_path, ide_chosen.get('key'))
    if (os.path.exists(ide_java_conf)):
        shutil.rmtree(ide_java_conf)

    print('Done! Reset {}'.format(ide_chosen.get('name')))

main()
