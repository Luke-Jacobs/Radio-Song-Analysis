from scripts.SongCollection import *
import signal, sys, os
import argparse


def getCommandLineArguments():
    # Commands
    ap = argparse.ArgumentParser('Radio Song Analysis')
    subparsers = ap.add_subparsers(dest='command')

    # Command - Analyze
    showParser = subparsers.add_parser('show', help='Show data, graphs, and analysis')  # TODO Add to this

    # Command - Collect
    collectParser = subparsers.add_parser('collect', help='Collect data over time')
    collectParser.add_argument('-i', '--input', type=str, required=False, default='new',
                    help='The timestamp of the collection to load. Use \'newest\' to load the most recently saved collection.')
    collectParser.add_argument('-w', '--wait', type=float, default=4, required=False,
                    help='The wait time to fetch the recent songs list.')
    collectParser.add_argument('-l', '--logDir', type=str, required=False, default=None,
                    help='Redirect the program\'s log to a file')
    collectParser.add_argument('-o', '--outputDir', type=str, required=False, default='data',
                    help='The folder to write the log files to')
    collectParser.add_argument('-b', '--background', action='store_true',
                    help='Move the process into the background')
    return ap.parse_args()


def temp():
    c = StationPlayCollection.getMostRecentSaved()
    c['KLOVE'].showFrequencyBoxAndWhisker()


if __name__ == '__main__':
    # temp()

    # Arguments
    args = getCommandLineArguments()

    # Establish CTRL-C handler
    def signal_handler(sig, frame):
        print('Saving collection and quitting...')
        if COLLECTION is not None:
            COLLECTION.save()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    # Handle collection
    if args.command == 'collect':

        # Input
        if args.input == 'newest':
            COLLECTION = StationPlayCollection.getMostRecentSaved()
        elif args.input == 'new':
            COLLECTION = StationPlayCollection()
        else:
            timestamp = None
            try:
                timestamp = int(args.input)
            except ValueError:
                print('[-] Input file must be in integer format!')
                exit(-1)
            print('[i] Restoring %d' % timestamp)
            COLLECTION = StationPlayCollection.restore(timestamp)

        FETCH_WAIT = args.wait

        if args.background:
            print('[i] Moving into the background')
            if os.fork():
                sys.exit()

        if args.logDir:
            print('[i] Redirecting program output to %s' % args.logDir)
            sys.stdout = open(args.logDir, 'w+', 1)

        # Start collecting
        collectSongsFromStations(COLLECTION, wait=args.wait*60, folder=args.outputDir)

    # Handle showing
    elif args.command == 'show':
        print(args)

