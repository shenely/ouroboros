# built-in libraries
import datetime

# external libraries
# ...

# internal libraries
# ...

# exports
__all__ = ("getdata", "f10p7")

data = []


def lerp(v0, v1, t):
    return (1 - t) * v0 + t * v1


def getdata():
    global data
    with open("../dat/RecentIndices.txt") as f:
        for line in f:
            if not line.startswith(":") and not line.startswith("#"):
                parts = line.split()
                dt = datetime.datetime(int(parts[0]), int(parts[1]), 15, 12)
                f10p7 = float(parts[8])
                if f10p7 != -1.0:  # Missing or not applicable data:  -1
                    data.append({"dt": dt, "f10p7": f10p7})

    with open("../dat/Predict.txt") as f:
        for line in f:
            if not line.startswith(":") and not line.startswith("#"):
                parts = line.split()
                dt = datetime.datetime(int(parts[0]), int(parts[1]), 15, 12)
                f10p7 = float(parts[5])
                if f10p7 != -1.0:  # Missing or not applicable data:  -1
                    data.append({"dt": dt, "f10p7": f10p7})


def f10p7(dt):
    global data
    for i in range(1, len(data)):
        d0, d1 = data[i-1:i+1]
        if d0["dt"] < dt <= d1["dt"]:
            t = ((dt - d0["f10p7"]).total_seconds() /
                 (d1["f10p7"] - d0["f10p7"]).total_seconds())
            return lerp(d0["f10p7"], d1["f10p7"], t)
    else:
        raise Exception  # not in time range
