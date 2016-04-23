import json,time,datetime
import logging

#Taken from commanding/pop_Consts
YES = ["YES","Y","YUP","YOU BETCHYA","FUCK YEAH"]
NO = ["NO","N","HELL NO"]

UNIX = datetime.datetime(1970,1,1)
WEEK = datetime.timedelta(weeks=1)

SATELLITE_LIST = [
    'SkySat-1',
    'SkySat-2',
#    'SkySat-C1'
    ]

NOTEBOOK_LIST = [
    '01-Library.ipynb',
#    'ACS_Dump_Data.ipynb',
    'Anomalies.ipynb',
    'Avionics.ipynb',
    'EVR.ipynb',
    'Exceptions.ipynb',
    'GNC_Counters.ipynb',
    'GNC_Gps.ipynb',
    'GNC_Gyro.ipynb',
    'GNC_Mag.ipynb',
    'GNC_ReactionWheel.ipynb',
    'GNC_StarTracker.ipynb',
    'HDRS.ipynb',
    'Image_Storage.ipynb',
    'Limits.ipynb',
    'Orbit_TLE.ipynb',
    'PES_NAND.ipynb',
    'Power.ipynb',
    'Radios.ipynb',
#    'Systems.ipynb',
    'Thermal.ipynb',
    ]

AUTHORIZED_NOTEBOOKS = ['Limits.ipynb']

WAIT_TIME = 10

#Adapted from commanding/pop_Utils
def ask(prompt):
    """Prompt user with a yes/no question"""
    ans = raw_input(prompt).upper()

    while ans not in (YES + NO):
        ans = raw_input("Respond Y or N to: %s" % prompt).upper()

    if ans in YES:
        return True
    elif ans in NO:
        return False

def default(obj):
    """Include date/times in JSON encoder"""
    if isinstance(obj,datetime.datetime):
        obj = { "$datetime": (obj - UNIX).total_seconds() }
    elif isinstance(obj,datetime.date):
        obj = { "$date": (obj - UNIX.date()).total_seconds() }
    elif isinstance(obj,datetime.time):
        obj = { "$time": (obj - UNIX.time()).total_seconds() }
    elif isinstance(obj,datetime.timedelta):
        obj = { "$elapsed": obj.total_seconds() }
    else:
        obj = json.JSONEncoder.default(obj)

    return obj

def pipe_check(pipe_list,logger,wait=WAIT_TIME):
    """Check subprocess types to see if they're running"""
    while len(pipe_list) > 0:
        for i in range(len(pipe_list)-1,-1,-1):
            nb,pipe = pipe_list[i]

            if pipe.poll() is not None:
                logging.info("%s has complete!" % nb)
                pipe_list.pop(i)
        else:
            logging.info("Waiting on %i notebooks..." % len(pipe_list))
            time.sleep(wait)
    else:
        logging.info("All notebooks complete!")

def trending_filepath(name,start,end,nb):
    """Format filepath for trending results"""
    return "/".join(["Trending",
                     name,
                     "%s+%dd" % (start.strftime("%Y-%m-%d"),
                                 (end - start).total_seconds() / (24 * 60 * 60)),
                     ".".join([nb.split(".")[0],"html"])])