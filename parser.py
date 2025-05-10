import os
import json
import statistics
from datetime import datetime

import matplotlib.pyplot as plt

runs_path = "C:/Program Files (x86)/Steam/steamapps/common/SlayTheSpire/runs"


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
                        yield data
                except FileNotFoundError:
                    print(f'Error: File not found at {file_path}')
                except json.JSONDecodeError:
                    print(f'Error: Could not decode JSON from {file_path}')
                except Exception as e:
                    print(f'Error occured while processing {file_path}: {e}')


def run_filter(run):
    if run.get('ascension_level') != 20:
        return False
    char = run.get('character_chosen')
    if char not in ['IRONCLAD', 'THE_SILENT', 'DEFECT', 'WATCHER']:
        return False
    if run.get('floor_reached') < 2:
        return False
    return True


def duration_format(seconds):
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    return f'{hrs:02}:{mins:02}:{secs:02}'


def average_floor_data(runs, run_qty):
    x_vals = []
    y_vals = []
    for n in range(run_qty-1, len(runs)):
        floors = [1 if r['victory'] else 0 for r in runs[n-run_qty+1:n+1]]
        x_vals.append(n)  # runs[n]['local_time'])
        y_vals.append(statistics.mean(floors))
    return x_vals, y_vals


if __name__ == '__main__':
    def sort_key(run):
        return run['local_time']
    data = sorted(list(filter(run_filter, runs())), key=sort_key)
    wins = 0
    for run in data:
        print(f"{run['local_time']}, {run['playtime']}, {run['max_hp']}, "
              f"{run['deck_size']}, {run['floor_reached']}, {run['victory']}, "
              f"{run['character_chosen']}")
        if run['victory']:
            wins += 1
    print(wins / len(data))
    plt.plot(*average_floor_data(data, 50))
    plt.show()
