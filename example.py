import time


def func(x):
    time.sleep(x)


def main():
    for x in [0.1, 0.2, 0.3]:
        func(x)

    time.sleep(0.5)


if __name__ == '__main__':
    main()
