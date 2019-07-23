# built-in libraries
import argparse

# external libraries
# ...

# internal libraries
from ouroboros.util import parse_time, parse_rate

# exports
__all__ = ("init",)

# constants
# ...


def init():
    parser = argparse.ArgumentParser(prog="ouroboros")

    parser.add_argument("-a", "--auto", action="store_true",
                        help="auto start")
    parser.add_argument("-t", "--time", type=parse_time, default=0.0,
                        help="wall time")
    parser.add_argument("-x", "--rate", type=parse_rate, default=1.0,
                        help="clock rate")
    parser.add_argument("-r", "--rest", action="store_true",
                        help="rest api")
    parser.add_argument("filename",
                        help="simulation definition (yaml)")

    return parser.parse_args()
