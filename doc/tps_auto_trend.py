#!/usr/bin/python

import sys
import subprocess
import argparse
import logging
import datetime

from AutoTrend_Utils import *

# Total Runtime for all notebooks (without limits and thermal)
# is roughly 32 min 20 sec for "SS1 Sep 2015"

def main():
    start = datetime.datetime.now()

    logger = logging.getLogger("auto_trend")

    #Default trend 5 weeks in the past (~month)
    now = datetime.datetime.now().date()
    past = now - 5 * WEEK

    #Release the parser!
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--sat-name",
                        choices=SATELLITE_LIST,
                        required=True,dest="name",
                        help='name of the satellite')
    parser.add_argument("-b","--start-date",
                        type=lambda x:datetime.datetime.strptime(x,"%Y-%m-%d"),
                        default=past,dest="start",
                        help='start time for trending (YYYY-MM-DD)')
    parser.add_argument("-e","--end-date",
                        type=lambda x:datetime.datetime.strptime(x,"%Y-%m-%d"),
                        default=now,dest="end",
                        help='end time for trending (YYYY-MM-DD)')
    parser.add_argument("-z","--auth-code",
                        action="count",dest="auth",
                        help='authorization level')
    parser.add_argument("ipynbs",nargs="+",
                        choices=NOTEBOOK_LIST,
                        help="list of notebooks to run")
    args = parser.parse_args(sys.argv[1:])

    #JSON to replace the god forsaken file
    data = {
        "name": args.name,
        "start": args.start,
        "end": args.end
    }

    with open("sat_data.json", 'w') as fout:
        json.dump(data,fout,default=default)

    pipe_list = []

    #Prompt if the user really wants to run thus (unless authorized)
    if args.auth >= 1 or ask("Are you sure you want to run trending? "):
        #Always run 01-Library first if it's in the list of notebooks
        if NOTEBOOK_LIST[0] in args.ipynbs:
            nb = NOTEBOOK_LIST[0]

            args.ipynbs.remove(nb)

            res_path = trending_filepath(args.name,args.start,args.end,nb)
            cmd_str = " ".join(["tps_report.py","-o",res_path,nb])

            pipe = subprocess.Popen(cmd_str,shell=True)
            pipe_list.append([nb,pipe])
            pipe_check(pipe_list,logger)

        #Check for notebooks that require authorization
        if args.auth < 2:
            for nb in AUTHORIZED_NOTEBOOKS:
                if nb in args.ipynbs and \
                   not ask("Are you authorized to run %s (be honest)? " % nb):
                    args.ipynbs.remove(nb)#remove them if not

        #Where the magic happens
        for nb in args.ipynbs:
            res_path = trending_filepath(args.name,args.start,args.end,nb)
            cmd_str = " ".join(["tps_report.py","-o",res_path,nb])

            logging.info("Executing notebook %s..." % nb)
            pipe = subprocess.Popen(cmd_str,shell=True)
            pipe_list.append([nb,pipe])
        else:
            pipe_check(pipe_list,logger)

    end = datetime.datetime.now()

    logging.warning("Trending took %.4f minutes!" % ((end - start).total_seconds() / 60))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    main()