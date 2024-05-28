import sys
import yaml
import yaml_include
from pathlib import Path
import re
import more_itertools

yaml.add_constructor('!include', yaml_include.Constructor())

with open('config.yaml') as file:
    mainConfig = yaml.full_load(file)

configs = sys.argv[1] if len(sys.argv) > 1 else mainConfig['files']

for config in configs:
    print('Processing ' + config + '...')
    with open(config) as file:
        config = yaml.full_load(file)

        playlist = []

        includes = []
        for include in list(more_itertools.collapse(config['include'] or [])):
            includes.append(re.compile(
                '.*' + include + '.*', flags=re.IGNORECASE))

        excludes = []
        for exclude in list(more_itertools.collapse(config['exclude'] or [])):
            excludes.append(re.compile(
                '.*' + exclude + '.*', flags=re.IGNORECASE))

        root = Path(config['root'])
        for path, _, files in root.walk():
            for file in files:
                fileName = (path / file).relative_to(root).as_posix()
                useFile = False
                for include in includes:
                    if include.match(fileName):
                        useFile = True
                        break
                for exclude in excludes:
                    if exclude.match(fileName):
                        useFile = False
                        break

                if useFile:
                    playlist.append(fileName)

        playlist.sort()
        with open(config['output'], mode="w") as output:
            for file in playlist:
                output.write(file + "\n")

