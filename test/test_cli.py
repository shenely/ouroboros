# built-in libraries
import sys

# external libraries
import pytest

# internal libraries
from ouroboros.cli import init

# constants
# ...


def test_init_empty(mocker):
    with pytest.raises(SystemExit):
        with (mocker.mock_module.patch.object
              (sys, "argv",
               ["__main__.py"])):
            ns = init()


def test_init_good(mocker):
    with (mocker.mock_module.patch.object
          (sys, "argv",
           ["__main__.py", "py.test"])):
        ns = init()
        assert ns.auto == False
        assert ns.time == 0.0
        assert ns.rate == 1.0
        assert ns.rest == False
        assert ns.filename == "py.test"


def test_init_bad(mocker):
    with pytest.raises(SystemExit):
        with (mocker.mock_module.patch.object
              (sys, "argv",
               ["__main__.py", "--test", "py.test"])):
            ns = init()


def test_auto_short(mocker):
    with (mocker.mock_module.patch.object
          (sys, "argv",
           ["__main__.py", "-a", "py.test"])):
        ns = init()
        assert ns.auto == True


def test_auto_long(mocker):
    with (mocker.mock_module.patch.object
          (sys, "argv",
           ["__main__.py", "--auto", "py.test"])):
        ns = init()
        assert ns.auto == True


def test_time_short(mocker):
    with (mocker.mock_module.patch.object
          (sys, "argv",
           ["__main__.py", "-t", "1234567890", "py.test"])):
        ns = init()
        assert ns.time == 1234567890


def test_time_long(mocker):
    with (mocker.mock_module.patch.object
          (sys, "argv",
           ["__main__.py", "--time", "1234567890", "py.test"])):
        ns = init()
        assert ns.time == 1234567890


def test_rate_short(mocker):
    with (mocker.mock_module.patch.object
          (sys, "argv",
           ["__main__.py", "-x", "10", "py.test"])):
        ns = init()
        assert ns.rate == 10


def test_rate_long(mocker):
    with (mocker.mock_module.patch.object
          (sys, "argv",
           ["__main__.py", "--rate", "10", "py.test"])):
        ns = init()
        assert ns.rate == 10


def test_rest_short(mocker):
    with (mocker.mock_module.patch.object
          (sys, "argv",
           ["__main__.py", "-r", "py.test"])):
        ns = init()
        assert ns.rest == True


def test_rest_long(mocker):
    with (mocker.mock_module.patch.object
          (sys, "argv",
           ["__main__.py", "--rest", "py.test"])):
        ns = init()
        assert ns.rest == True
