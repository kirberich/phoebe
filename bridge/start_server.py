#!/usr/bin/env python

import argparse

from device_servers import (
    HueServer,
    OrviboServer,
    WeMoServer,
    AppleTVServer,
)

SERVERS = {
    'hue': HueServer,
    'orvibo': OrviboServer,
    'wemo': WeMoServer,
    'appletv': AppleTVServer,
}


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Start device server.')
    parser.add_argument('server', choices=SERVERS.keys())

    return parser.parse_args()


if __name__ == '__main__':
    """Start a device server."""
    args = parse_args()

    server = SERVERS[args.server]()
    server.start()
