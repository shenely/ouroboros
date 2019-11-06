# built-in libraries
import sys
import time
import heapq
import collections
import itertools
import asyncio
import logging

# external libraries
import yaml

# internal libraries
from ouroboros.conf import INFINITY
from ouroboros.core import Item, run
import ouroboros.cli as cli
import ouroboros.rest as rest
import ouroboros.ext as _  # noqa

# constants
# ...


def init(ns):
    """init func"""
    with open(ns.filename, "r") as stream:
        sim = yaml.load(stream, Loader=yaml.Loader)

    # first pass - populate internals
    logger.info("1st pass - populate internals")
    lake = {model["name"]: {name:
                            (logger.debug("populate %s in %s",
                                          name[0], name[1])
                             or (Item(**item)
                                 if item is not None
                                 else None))
                            for (name, item)
                            in list(model["items"].items())}
            for model in sim}
    logger.info("done 1st pass")

    # second pass - reference externals
    logger.info("2nd pass - reference externals")
    any(lake[_id].update({name:
                          (logger.debug("reference %s from %s to %s",
                                        name[0], name[1], _id)
                           or lake[name[0]].get((False, name[1])))
                          for name in list(lake[_id].keys())
                          if name[0] in lake})
        for _id in lake)
    logger.info("done 2nd pass")

    # third pass - start tasks
    logger.debug("3rd pass - start tasks")
    tasks = (logger.debug("start %s in %s",
                          task["tag"], model["name"])
             or run(task, lake[model["name"]])
             for model in sim
             for task in model["procs"])
    logger.info("done 3rd pass")

    lake[None][True, None].data[None] = tasks  # to be popped

    return lake


async def main(pool):
    """main loop"""
    lake[None][False, None].data["a"] = ns.auto
    lake[None][False, None].data["t"] = ns.time
    lake[None][False, None].data["x"] = ns.rate
    
    lake[None][True, None].data["e"] = e = set()  # event set
    lake[None][True, None].data["q"] = q = collections.deque()  # task queue
    lake[None][True, None].data["z"] = z = []  # clock time
    
    lake[None][True, None].data["f"] = asyncio.Future()
    if lake[None][False, None].data["a"]:  # auto start
        lake[None][True, None].data["t"] = time.time()
        lake[None][True, None].data["f"].set_result(True)
    else:
        logger.warning("auto start disabled")
    await pool[True, None].data["f"]

    any(pool[True, None].data.pop(None))

    t = pool[False, None].data["t"]  # wall time
    heapq.heappush(z, (-INFINITY,  # init event
                       hash(pool[False, None].ctrl[False]),
                       pool[False, None].ctrl[False]))
    heapq.heappush(z, (t + sys.float_info.epsilon,  # main event
                       hash(pool[False, None].ctrl[True]),
                       pool[False, None].ctrl[True]))

    while True:
        any(e.add(heapq.heappop(z)[2])
            for i in range(len(z))
            if z[0][0] <= t)
        any(q.append(cb)
            for ev in e
            for cb in ev.cbs)  # time event
        while len(q) > 0:
            task = q.popleft()
            # XXX controls events and callbacks
            # ... events may only occur once per clock cycle
            # ... one instance of callback may be in queue
            # ... bool events add callbacks to queue
            # ... truthy events are recorded
            # ... falsey events are not recorded
            # ... numeric events are added to clock
            any(heapq.heappush(z, (s, hash(ev), ev))
                if not isinstance(s, bool)
                else ((any(q.append(cb)
                           for cb in ev.cbs)
                       if ev not in e
                       else None)
                      or (not s or e.add(ev)))
                for (ev, s) in itertools.chain
                (*(logger.info("exec %s", task.tag)
                   or task.gen.send(e))))
            await pool[True, None].data["f"]
        else:
            e.clear()
        T, t0, x = (pool[True, None].data["t"],
                    pool[False, None].data["t"],
                    pool[False, None].data["x"])
        logger.info("exec time: %.4f", time.time() - T)
        if len(z) > 0 and x > 0.0:
            t = z[0][0]  # wall time
            T += (t - t0) / x  # real time
            if T > time.time():
                await asyncio.sleep(T - time.time())
            logging.debug("wall time: %.4f", t)
        else:
            T = time.time()  # real time
            pool[True, None].data["f"] = asyncio.Future()
        pool[True, None].data["t"] = T  # real time
        pool[False, None].data["t"] = t  # wall time
        await pool[True, None].data["f"]


if __name__ == "__main__":
    ns = cli.init()
    
    # logging
    level = (logging.ERROR
             if ns.verbose == 0 else
             logging.WARNING
             if ns.verbose == 1 else
             logging.INFO
             if ns.verbose == 2 else
             logging.DEBUG)
    logging.basicConfig(format="(%(asctime)s) [%(levelname)s] %(message)s",
                        datefmt="%Y-%m-%dT%H:%M:%SL",
                        level=level)
    logger = logging.getLogger(__name__)

    lake = init(ns)
    if ns.rest:
        rest.init(lake)
    else:
        logger.warning("rest api disabled")

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main(lake[None]))
    except KeyboardInterrupt:
        logger.info("closing")
    finally:
        loop.close()
