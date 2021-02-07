## Lineprof

A simplified version of Robert Kern's [line profiler](https://github.com/rkern/line_profiler)

### Usage

```
usage: lineprof.py [-h] [-m] [-o OUTPUT] [--include INCLUDE] prog ...

Line profiler

positional arguments:
  prog                  A script to profile
  args                  Arguments for a script

optional arguments:
  -h, --help            show this help message and exit
  -m                    Profile a module
  -o OUTPUT, --output OUTPUT
                        Write output to file
  --include INCLUDE     File(s) to trace (glob is supported)
```

### Example

example.py
```python
import time


def func(x):
    time.sleep(x)


def main():
    for x in [0.1, 0.2, 0.3]:
        func(x)

    time.sleep(0.5)


if __name__ == '__main__':
    main()
```

Output:
<p align="center">
  <img src="https://github.com/qweeze/lineprof/raw/master/example.png?raw=true" width=100% alt="screenshot"/>
</p>
