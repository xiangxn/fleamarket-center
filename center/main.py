import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "rpc"))

import argparse
import getpass
import json
from center import metadata
from center.server import bits_flea_run
from center.syncsvr import SyncSvr



def main(argv):
    """Program entry point.

    :param argv: command-line arguments
    :type argv: :class:`list`
    """
    author_strings = []
    for name, email in zip(metadata.authors, metadata.emails):
        author_strings.append('Author: {0} <{1}>'.format(name, email))

    epilog = '''
{project} {version}

{authors}
URL: <{url}>
'''.format(
        project=metadata.project,
        version=metadata.version,
        authors='\n'.join(author_strings),
        url=metadata.url)

    arg_parser = argparse.ArgumentParser(
        prog=argv[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=metadata.description,
        epilog=epilog)
    arg_parser.add_argument(
        '--config', type=argparse.FileType('r'),
        help='config file for center')
    arg_parser.add_argument(
        'command',
        choices=['grpc','sync'], nargs='?',
        help='the command to run')
    arg_parser.add_argument(
        '-V', '--version',
        action='version',
        version='{0} {1}'.format(metadata.project, metadata.version))
    arg_parser.add_argument(
        '-I', '--init', action='store_true',
        help='Whether to sync initial data?')

    args = arg_parser.parse_args(args=argv[1:])
    config_info = procConfig(args.config)
    if args.command == "grpc":
        bits_flea_run(config_info)
    elif args.command == "sync":
        ss = SyncSvr(config_info, args.init)
        ss.Run()
    else:
        print(epilog)
    return 0

def procConfig(cf):
    config_info = {}
    if not cf:
        cf = open("./config.json","r")
    config_info = json.load(cf)
    # if config_info["encrypt"] == 0 :
    #     enc = getpass.getpass("Please enter your password to encrypt your private key: ")
    #     objAES = PYCrypt(enc)
    #     for k in config_info:
    #         if "_wif" in k:
    #             config_info[k] = objAES.encrypt(config_info[k])
    #     if "gateways" in config_info and len(config_info['gateways'])>0:
    #         for item in config_info['gateways']:
    #             for k in item:
    #                 if k == "wif":
    #                     item[k] = objAES.encrypt(item[k])
    #     config_info["encrypt"] = 1
    #     with open(cf.name,"w") as f:
    #         json.dump(config_info,f)
    #         sys.exit(1)
    # else:
    #     enc = getpass.getpass("Please enter your password: ")
    #     objAES = PYCrypt(enc)
    #     for k in config_info:
    #         if "_wif" in k:
    #             config_info[k] = objAES.decrypt(config_info[k])
    #     if "gateways" in config_info and len(config_info['gateways'])>0:
    #         for item in config_info['gateways']:
    #             for k in item:
    #                 if k == "wif":
    #                     item[k] = objAES.decrypt(item[k])
        #print(config_info['gateways'][0]['wif'])
    return config_info



def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()