#!/usr/local/bin/python3.8
import argparse
from datetime import date


if __name__=="__main__":
    today = date.today()
    td = today.strftime("%Y%m%d")

    parser = argparse.ArgumentParser(description='Process Fiber Test')
    parser.add_argument('--id', dest='id', type=int,  default=-1, help='Set fiber ID, default to -1')
    parser.add_argument('--suffix', dest='suffix', default="", help='Suffix to file name prefix_id_suffix.csv, default to None')
    parser.add_argument('--prefix', dest='prefix', default="fibertest", help='Prefix to file name prefix_id_suffix.csv, default to fibertest')

    default_path="./data/%s/"%td
    parser.add_argument('--save_dir', dest='save_dir', default=default_path, help='Saving directory, default to %s'%default_path)

    parser.add_argument('--rep', dest='rep', default=5, type=int, help='Number of rail passes')
    parser.add_argument('--n', dest='n', default=5, type=int, help='Number of accumulated measurements')
    parser.add_argument('--pos', dest='str_pos', default=None,help="Positions for one pass")
    parser.add_argument('--config',dest='config_file',default="config/default.txt", help="An external configuration file to set the positions, if --pos is set, --pos take precedence.")

    args = parser.parse_args()

    print(args.id)

    positions = list()
    if args.str_pos is not None:
        positions = list(map(int,args.str_pos.split(",")))
        print("Set positions from command line")
    else:
        with open(args.config_file) as f:
            positions = list( map(int, f.readline().split(",")))
            print("Set positions from config file %s"%args.config_file)
    print("Positions are %s"%(",".join(map(str,positions))))
        


    import DAQ
    daq = DAQ.DAQ(args.rep)
    daq.n_measurements = args.n
    daq.fiber_id = args.id
    daq.SetSaveDirectory( args.save_dir )
    suffix = None if args.suffix == "" else args.suffix
    daq.RunDAQ(args.id, args.rep, args.save_dir, args.prefix, suffix,positions)

