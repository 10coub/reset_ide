import os
import re
import argparse
import subprocess
import shutil
import getpass

def get_versions(path, ide_prefix):
    versions = []
    for directory in os.listdir(path):
        if re.match(rf'^{ide_prefix}*', directory):
            versions.append(directory)
    return versions

def get_current_version(path, ide_prefix):
    result = ''
    versions = get_versions(path, ide_prefix)
    if (len(versions) > 0):
        versions.sort()
        result = versions[-1]
    return result

def remove_files_by_pattern(dir_path, pattern):
    for f in os.listdir(dir_path):
        if re.search(pattern, f):
            os.remove(os.path.join(dir_path, f))

def remove_lines_by_pattern(file_name, pattern):
    updateLines = []
    with open(file_name, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if re.search(pattern, line):
                continue
            updateLines.append(line)

    if len(updateLines) > 0:
        with open(file_name, 'w') as file:
            file.writelines(updateLines)

def main():
    parser = argparse.ArgumentParser(description='Reset IDE')
    parser.add_argument(
        '-i', '--ide', type=str, required=False,
        help='IDE name, example: phpstorm')
    args = parser.parse_args()
    ide_name = args.ide

    if (not ide_name):
        print('Input IDE name, example: phpstorm')
        ide_name = str(input())

    ide_name = ide_name.lower()
    ide_prefix = ''
    if ide_name == 'clion':
        ide_prefix = 'CLion'
    elif ide_name == 'goland':
        ide_prefix = 'GoLand'
    elif ide_name == 'phpstorm':
        ide_prefix = 'PhpStorm'
    elif ide_name == 'datagrip':
        ide_prefix = 'DataGrip'
    elif ide_name == 'intellij-idea-ultimate':
        ide_prefix = 'IntelliJIdea'

    if (not ide_prefix):
        print('Not found support IDE')
        exit()

    username = getpass.getuser()
    home_path = f'/home/{username}'
    if (not os.path.exists(home_path)):
        print('Not found user home path.')
        exit()

    config_path = f'{home_path}/.config/JetBrains'
    if (not os.path.exists(config_path)):
        print('Not found config IDE. This script works with JetBrains IDEs are older than 2020')
        exit()

    current_version = get_current_version(config_path, ide_prefix)
    if (not current_version):
        print('Not found current IDE version')
        exit()

    config_ide_path = '{}/{}'.format(config_path, current_version)

    try:
        evaluation_folder = '{}/eval/'.format(config_ide_path)
        remove_files_by_pattern(evaluation_folder, '([a-zA-Z0-9]+)\.evaluation.key')
    except Exception as e:
        print('Not remove evaluation keys, error: ' + str(e))
        exit()

    try:
        other_xml = '{}/options/other.xml'.format(config_ide_path)
        remove_lines_by_pattern(other_xml, 'evlsprt')
    except Exception as e:
        print('Not remove lines in other.xml, error: ' + str(e))
        exit()

    try:
        ide_java_conf = f'{home_path}/.java/.userPrefs/jetbrains/{ide_name}/'
        shutil.rmtree(ide_java_conf)
    except Exception as e:
        print('Not remove java settings, error: ' + str(e))
        print('Maybe the script worked correctly, check your IDE')
        exit()

    print(f'Done! Reset {ide_name}!')

main()
