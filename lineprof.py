import argparse
import glob
import io
import math
import os
import runpy
import shutil
import statistics
import sys
import time
from collections import defaultdict
from warnings import warn


def make_tracer(filenames):
    samples = defaultdict(list)
    last_time = {}

    def tracer(frame, event, arg):
        if event == 'call':
            filename = frame.f_code.co_filename
            if not os.path.isabs(filename):
                filename = os.path.abspath(filename)

            if filename not in filenames:
                return None

        elif event == 'line' or event == 'return':
            ts = time.perf_counter()

            if frame.f_code in last_time:
                old_line_no, old_time = last_time[frame.f_code]
                samples[(frame.f_code.co_filename, old_line_no)].append(ts - old_time)

            if event == 'line':
                last_time[frame.f_code] = frame.f_lineno, ts
            else:
                last_time.pop(frame.f_code, None)

        return tracer

    return tracer, samples


def aggregate(samples):
    aggregated = defaultdict(dict)

    for (filename, line_no), tseries in samples.items():
        aggregated[filename][line_no] = (
            len(tseries),
            math.fsum(tseries),
            statistics.mean(tseries),
        )

    return aggregated


def format_output(stats):
    out = io.StringIO()
    for filename, line_stats in stats.items():
        if not os.path.exists(filename):
            warn(f'Could not read {filename}')

        with open(filename) as fp:
            header = f'Hits |Sum  |Avg  | {filename}'
            border = '=' * shutil.get_terminal_size().columns
            out.write(f'{border}\n{header}\n{border}\n')

            for line_no, line in enumerate(fp):
                stats = line_stats.get(line_no + 1)
                if stats is not None:
                    n_hits, total_time, av_time = stats
                    out.write(f'{n_hits:<5}|{total_time * 1e3:<5.0f}|{av_time * 1e3:<5.0f}| ')
                else:
                    out.write('     |     |     | ')

                out.write(line)

    return out.getvalue()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Line profiler')
    parser.add_argument('-m', action='store_true', help='Profile a module', default=False)
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), default='-', help='Write output to file')
    parser.add_argument('--include', type=str, default=None, help='File(s) to trace (glob is supported)')
    parser.add_argument('prog', help='A script to profile')
    parser.add_argument('args', nargs='...', help='Arguments for a script')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(0)

    args = parser.parse_args()

    sys.argv[:] = [args.prog, *args.args]
    sys.path.insert(0, os.path.dirname(args.prog))

    if args.include is not None:
        filenames = frozenset(map(os.path.abspath, glob.iglob(args.include)))
    else:
        filenames = frozenset([os.path.abspath(args.prog)])

    tracer, samples = make_tracer(filenames)
    sys.settrace(tracer)
    try:
        if args.m:
            runpy.run_module(args.prog, run_name='__main__')
        else:
            runpy.run_path(args.prog, run_name='__main__')

    finally:
        sys.settrace(None)
        stats = aggregate(samples)
        args.output.write(format_output(stats))
