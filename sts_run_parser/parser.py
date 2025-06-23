import os
import hashlib
import json
import statistics
from datetime import datetime
from functools import wraps

runs_path = "C:/Program Files (x86)/Steam/steamapps/common/SlayTheSpire/runs"


def get_directory_hash(directory):
    hasher = hashlib.md5()
    for root, _, files in os.walk(directory):
        for name in sorted(files):
            filepath = os.path.join(root, name)
            try:
                hasher.update(filepath.encode('utf-8'))
                mtime = os.path.getmtime(filepath)
                hasher.update(str(mtime).encode('utf-8'))
            except OSError:
                pass
    return hasher.hexdigest()


def cache_on_directory_change(directory):
    def decorator(generator_func):
        cached_data = []
        last_hash = None

        @wraps(generator_func)
        def wrapper(*args, **kwargs):
            nonlocal cached_data, last_hash
            current_hash = get_directory_hash(directory)

            if current_hash != last_hash:
                cached_data = list(generator_func(*args, **kwargs))
                last_hash = current_hash

            return cached_data
        return wrapper
    return decorator


@cache_on_directory_change(runs_path)
def runs():
    for dirpath, dirnames, filenames in os.walk(runs_path):
        for filename in filenames:
            if filename.endswith('.run'):
                file_path = os.path.join(dirpath, filename)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        data['local_time'] = datetime.strptime(
                            data['local_time'], '%Y%m%d%H%M%S')
                        data['playtime'] = duration_format(data['playtime'])
                        data['deck_size'] = len(data['master_deck'])
                        data['max_hp'] = data['max_hp_per_floor'][-1]
                        data['victory'] = data['floor_reached'] == 57
                        yield data
                except FileNotFoundError:
                    print(f'Error: File not found at {file_path}')
                except json.JSONDecodeError:
                    print(f'Error: Could not decode JSON from {file_path}')
                except Exception as e:
                    print(f'Error occured while processing {file_path}: {e}')


def run_filter(char_filter):
    def filter_func(run):
        if run.get('ascension_level') != 20:
            return False
        char = run.get('character_chosen')
        if char not in ['IRONCLAD', 'THE_SILENT', 'DEFECT', 'WATCHER']:
            return False
        if char_filter != 'ALL' and char != char_filter:
            return False
        if run.get('floor_reached') < 2:
            return False
        if run.get('is_daily'):
            return False
        return True
    return filter_func


def duration_format(seconds):
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    return f'{hrs:02}:{mins:02}:{secs:02}'


def average_floor_data(run_qty, char='ALL'):
    def sort_key(run):
        return run['local_time']

    all_runs = sorted(list(filter(run_filter(char), runs())), key=sort_key)
    x_vals, winrate, avg_floor = [], [], []
    for n in range(run_qty-1, len(all_runs)):
        run_set = all_runs[n-run_qty+1:n+1]
        x_vals.append(n + 1)
        floors = [100 if r['victory'] else 0 for r in run_set]
        winrate.append(statistics.mean(floors))
        floors = [r['floor_reached'] for r in run_set]
        avg_floor.append(statistics.mean(floors))
    return [{
                'run': x_vals[n],
                'winrate': winrate[n],
                'avg_floor': avg_floor[n]
            } for n in range(len(x_vals))]


def best_streak(runs):
    streak = 0
    best_streak = 0
    for run in runs:
        if run['victory']:
            streak += 1
            if streak > best_streak:
                best_streak = streak
        else:
            streak = 0
    return best_streak
