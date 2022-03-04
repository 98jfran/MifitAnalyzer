import argparse
import json
import os
import sys
import logging
from standalone import Standalone

from utils import Utils

def start(args):
    Utils.setup_custom_logger()
    Utils.setup_case()
    
    logging.info("Starting Mifit analysis...")

    # Analysis logic

    standalone = Standalone(args.path, args.output)
    standalone.analyse()
    standalone.report()
    logging.info("Done")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MiFit Analyzer')
    parser.add_argument('-p', '--path', help='Dump app data', required = True)
    parser.add_argument('-o', '--output', help='Report output path folder', required = False)
    args = parser.parse_args()
    
    start(args)