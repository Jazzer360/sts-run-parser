import os
import json
import statistics
from datetime import datetime

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
                        data['victory'] = data['floor_reached'] == 57
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
    if run.get('is_daily'):
        return False
    return True


def duration_format(seconds):
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    return f'{hrs:02}:{mins:02}:{secs:02}'


def average_floor_data(runs, run_qty, char='ALL'):
    def char_filter(run):
        if char == 'ALL' or run.get('character_chosen') == char:
            return True
        else:
            return False
    runs = list(filter(char_filter, runs))
    x_vals, winrate, avg_floor = [], [], []
    for n in range(run_qty-1, len(runs)):
        last_qty = runs[n-run_qty+1:n+1]
        x_vals.append(n)
        floors = [1 if r['victory'] else 0 for r in last_qty]
        winrate.append(statistics.mean(floors))
        floors = [r['floor_reached'] / 57 for r in last_qty]
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
