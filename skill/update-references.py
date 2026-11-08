#!/usr/bin/env python3
"""Fetch the latest public Spikee main branch for this skill's reference files."""
from pathlib import Path
import subprocess


def update():
    destination = Path(__file__).resolve().parent / 'spikee-src'
    url = 'https://github.com/ReversecLabs/spikee.git'
    if not destination.exists():
        subprocess.run(['git', 'clone', '--depth', '1', '--branch', 'main', url, str(destination)], check=True)
    else:
        if not (destination / '.git').exists():
            raise SystemExit('Reference folder has no Git metadata; move it aside before refreshing.')
        dirty = subprocess.check_output(['git', '-C', str(destination), 'status', '--porcelain'], text=True)
        if dirty.strip():
            raise SystemExit('Reference source has local changes; preserve them before refreshing.')
        subprocess.run(['git', '-C', str(destination), 'fetch', '--depth', '1', url, 'main'], check=True)
        subprocess.run(['git', '-C', str(destination), 'checkout', '--detach', 'FETCH_HEAD'], check=True)
    revision = subprocess.check_output(['git', '-C', str(destination), 'rev-parse', 'HEAD'], text=True).strip()
    print('Spikee reference source: ' + revision)


if __name__ == '__main__':
    update()
