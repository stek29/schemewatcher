#!/usr/bin/env python3

import datetime
import os
import shutil
import subprocess
import sys
from difflib import unified_diff
from pathlib import Path

import requests

CHAT_ID = os.environ['CHAT_ID']
BOTAPI_BASE_URL = f"https://api.telegram.org/bot{os.environ['BOT_TOKEN']}/"


def parse_appcenter(appcenter_app_id):
    """ appcenter_app_id: {owner_name}/{app_name}/distribution_groups/{distribution_group_name} """
    list_url = f"https://install.appcenter.ms/api/v0.1/apps/{appcenter_app_id}/public_releases?scope=tester"
    latest = requests.get(list_url).json()[0]

    release_url = f"https://install.appcenter.ms/api/v0.1/apps/{appcenter_app_id}/releases/{latest['id']}"
    release_info = requests.get(release_url).json()

    version = f"Version {release_info['short_version']} ({release_info['version']})"
    return version, release_info['download_url']


def main():
    VERSION_FILE = 'latest_version.txt'
    try:
        with open(VERSION_FILE, 'r') as fd:
            current_version = fd.read().strip()
    except FileNotFoundError:
        current_version = 'unknown'

    new_version, apk_url = parse_appcenter(os.environ['APPCENTER_APP_ID'])
    print(new_version, apk_url)

    if new_version == current_version:
        return

    build_number = new_version.split('(')[1].split(')')[0]
    filename = 'tg_beta_{!s}.apk'.format(build_number)
    with open(filename, 'wb') as f:
        with requests.get(apk_url, stream=True) as r:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

    with open(filename+'.tl', 'w') as f:
        subprocess.run([
            'docker',
            'run',
            '-v',
            f'{Path(filename).resolve()}:/extractor/tandroid.apk',
            '--rm',
            'extract-tandroid',
        ], stdout=f, stderr=sys.stderr)

    os.remove(filename)

    lv = Path('latest_version.tl')
    nv = Path(filename+'.tl')
    if lv.exists():
        diff = [
            l
            for l in unified_diff(lv.read_text().split('\n'), nv.read_text().split('\n'))
            if l.startswith('-') or l.startswith('+')
        ]

        lv.unlink()

        print('diff', *diff, sep='\n')
        r = requests.post(
            BOTAPI_BASE_URL + 'sendDocument',
            data={
                'chat_id': CHAT_ID,
            },
            files={
                'document': (
                    'diff'+filename+'.txt',
                    '\n'.join(diff).encode(),
                    'text/plain',
                )
            }
        )
        print(r.json())

    version_info = '\n'.join(
        l for l in nv.read_text().split('\n') if l.startswith('//'))
    requests.post(
        BOTAPI_BASE_URL + 'sendDocument',
        data={
            'chat_id': CHAT_ID,
            'caption': version_info,
        },
        files={
            'document': (
                filename+'.tl',
                nv.read_bytes(),
                'text/plain',
            ),
        },
    )

    nv.rename('latest_version.tl')

    with open(VERSION_FILE, 'w') as fd:
        fd.write(new_version)


if __name__ == '__main__':
    main()
