#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
from getpass import getpass
import datetime
from datetime import datetime
from pathlib import Path
from frisenbriefbot.attachmentconvert import touchup
from itertools import repeat
import logging
from frisenbriefbot.messagefetch import fetch_messages
from frisenbriefbot.mailprocess import process_email
from tqdm import tqdm

from itertools import starmap

logger = logging.getLogger(__name__)

def process_messages(output_dir, messages):
    """Process messages concurrently"""
    # procfunc = partial(process_email, output_dir)
    for files in starmap(process_email, zip(repeat(output_dir), messages)):
        map(touchup, tqdm(files))


def main():
    logging.basicConfig(level=logging.INFO)

    # set up command line arguments
    parser = argparse.ArgumentParser(description="E-Mail Anhänge in LaTeX konvertieren")
    parser.add_argument(
        "--host", help="E-Mail Server (IMAP) das gescannt wird", type=str
    )
    parser.add_argument("--email", help="E-Mail Nutzer (Adresse)", type=str)
    parser.add_argument("--passwort", help="Password des kontos", type=str)
    parser.add_argument(
        "--datum",
        help="Datum, ab dem E-Mails gesucht werden. (Normalerweise Semesterbeginn)",
        type=str,
        metavar="TT-MM-JJJJ",
    )
    parser.add_argument("--output", default="output", type=Path)
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    args = parser.parse_args()

    # Ensure we write to our own empty directory
    os.makedirs(args.output)

    # prompt for missing variables interactively
    if args.host is None:
        args.host = input("IMAP Server: ")
    if args.email is None:
        args.email = input("E-Mail: ")
    if args.passwort is None:
        args.passwort = getpass()
    if args.datum is None:
        args.datum = input("Ab Datum (TT-MM-JJJJ): ")

    date = datetime.strptime(args.datum, "%d-%m-%Y").date()

    msgs = fetch_messages(args.host, args.email, args.passwort, date)

    process_messages(args.output, msgs)


if __name__ == "__main__":
    main()
