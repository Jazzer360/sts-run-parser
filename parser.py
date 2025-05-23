import os
import json
import statistics
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

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
    return x_vals, winrate, avg_floor, len(runs)


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


def plot_by_lookback(period):
    fig = plt.figure(
        label=f"Run data moving average (last {period} runs)")
    gs_main = gridspec.GridSpec(1, 2, width_ratios=[2, 1.5], figure=fig)

    vals, winrate, height, runs = average_floor_data(data, period)
    ax_main = fig.add_subplot(gs_main[0, 0])
    ax_main.plot(vals, winrate, label='Winrate')
    ax_main.plot(vals, height, label='Height reached')
    ax_main.set_title(f"Overall data ({runs})")
    ax_main.legend()

    gs_right = gridspec.GridSpecFromSubplotSpec(
        2, 2, subplot_spec=gs_main[0, 1], hspace=0.4, wspace=0.3)

    vals, winrate, height, runs = average_floor_data(data, period,
                                                     char='IRONCLAD')
    ax_ic = fig.add_subplot(gs_right[0, 0])
    ax_ic.plot(vals, winrate, label='Winrate')
    ax_ic.plot(vals, height, label='Height reached')
    ax_ic.set_title(f'Ironclad ({runs})')

    vals, winrate, height, runs = average_floor_data(data, period,
                                                     char='THE_SILENT')
    ax_ic = fig.add_subplot(gs_right[0, 1])
    ax_ic.plot(vals, winrate, label='Winrate')
    ax_ic.plot(vals, height, label='Height reached')
    ax_ic.set_title(f'Silent ({runs})')

    vals, winrate, height, runs = average_floor_data(data, period,
                                                     char='DEFECT')
    ax_ic = fig.add_subplot(gs_right[1, 0])
    ax_ic.plot(vals, winrate, label='Winrate')
    ax_ic.plot(vals, height, label='Height reached')
    ax_ic.set_title(f'Defect ({runs})')

    vals, winrate, height, runs = average_floor_data(data, period,
                                                     char='WATCHER')
    ax_ic = fig.add_subplot(gs_right[1, 1])
    ax_ic.plot(vals, winrate, label='Winrate')
    ax_ic.plot(vals, height, label='Height reached')
    ax_ic.set_title(f'Watcher ({runs})')


if __name__ == '__main__':
    def sort_key(run):
        return run['local_time']
    data = sorted(list(filter(run_filter, runs())), key=sort_key)
    lookback_period = 100

    print(f"Best Streak: {best_streak(data)}")

    plot_by_lookback(50)
    plot_by_lookback(100)
    plot_by_lookback(200)
    plt.show()
