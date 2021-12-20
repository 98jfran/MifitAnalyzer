import argparse
import os
import sys
import logging

from utils import Utils

def start(args):
    Utils.setup_custom_logger()
    Utils.setup_case()
    
    logging.info("Starting Mifit analysis...")
    
    if not args.output:
        args.output = os.path.join(Utils.get_base_path_folder(), "report")

    # Analysis logic

    logging.info("Done")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MiFit Analyzer')
    parser.add_argument('-p', '--path', help='Dump app data', required = False)
    parser.add_argument('-o', '--output', help='Report output path folder', required = False)
    args = parser.parse_args()
    
    start(args)