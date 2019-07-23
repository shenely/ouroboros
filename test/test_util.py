# built-in libraries
import datetime

# external libraries
import pytest

# internal libraries
from ouroboros.conf import ISO_8601, UNIX_EPOCH
from ouroboros.core import Type
from ouroboros.util import (coroutine,
                            default, object_hook,
                            parse_time, parse_rate)

# constants
# ...


def test_coroutine(mocker):
    wraps = mocker.patch("functools.wraps")
    dec = wraps.return_value = mocker.Mock()
    dec.side_effect = lambda x: x
    next = mocker.patch("ouroboros.util.next")
    func = mocker.Mock(["__name__", "__dict__", "__doc__"])
    func.__name__ = "test_coroutine"
    gen = func.return_value = mocker.Mock()
    wrapper = coroutine(func)
    wraps.assert_called_once_with(func)
    assert wrapper.__name__ == func.__name__
    assert wrapper.__dict__ == func.__dict__
    assert wrapper.__doc__ == func.__doc__
    cor = wrapper(1, 2, 3, a=True, b=False)
    func.assert_called_with(1, 2, 3, a=True, b=False)
    next.assert_called_once_with(gen)
    assert gen is cor
    

def test_default_good(mocker):
    df = mocker.Mock()
    oh = mocker.Mock()
    pytest = Type("py.test", "!py/test", bool, df, oh)
    obj = True
    default(obj)
    df.assert_called_once_with(obj)
    

def test_default_bad(mocker):
    df = mocker.Mock()
    oh = mocker.Mock()
    Type("py.test", "!py/test", bool, df, oh)
    obj = "py.test"
    with pytest.raises(TypeError):
        default(obj)
    

def test_object_hook_good(mocker):
    df = mocker.Mock()
    oh = mocker.Mock()
    Type("py.test", "!py/test", bool, df, oh)
    dct = {"py.test": True}
    object_hook(dct)
    oh.assert_called_once_with(dct)
    

def test_object_hook_bad(mocker):
    df = mocker.Mock()
    oh = mocker.Mock()
    pytest = Type("py.test", "!py/test", bool, df, oh)
    dct = {"pytest": True}
    obj = object_hook(dct)
    assert obj is dct


def test_parse_time_now(mocker):
    time = mocker.patch("time.time")
    now = time.return_value = mocker.Mock()
    t = parse_time("now")
    time.assert_called_once_with()
    assert t is now


def test_parse_time_unix():
    t = parse_time("1234567890")
    assert t == 1234567890


def test_parse_time_iso():
    s = "2000-01-01T00:00:00.000Z"
    dt = datetime.datetime.strptime(s, ISO_8601)
    t = parse_time(s)
    assert t == (dt - UNIX_EPOCH).total_seconds()


def test_parse_time_bad():
    with pytest.raises(ValueError):
        t = parse_time("py.test")


def test_parse_rate_rt():
    x = parse_rate("rt")
    assert x == 1.0


def test_parse_rate_sec():
    x = parse_rate("10")
    assert x == 10


def test_parse_rate_bad():
    with pytest.raises(ValueError):
        x = parse_rate("py.test")
