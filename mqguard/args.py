import argparse

def create_parser():
    parser = argparse.ArgumentParser(
        description="MQTT monitoring tool",
        epilog="Copyright (C) Ivo Slanina <ivo.slanina@gmail.com>",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-c', '--config',
                        help='path to configuration file',
                        default="/etc/mqguard.conf")
    parser.add_argument('-v', '--verbose',
                        help='verbose',
                        action='store_true')
    return parser

def parse_args():
    parser = create_parser()
    return parser.parse_args()
