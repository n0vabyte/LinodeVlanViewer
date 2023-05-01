#!/usr/bin/python3
# Hugs are worth more than handshakes

import requests
import json
from tabulate import tabulate
import argparse
import sys
import os

token_file = '/tmp/token'

class color:
    RED = '\033[91m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'    
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDCOLOR = '\033[0m'

# https://requests.readthedocs.io/en/latest/user/authentication/#new-forms-of-authentication
# https://stackoverflow.com/questions/29931671/making-an-api-call-in-python-with-an-api-that-requires-a-bearer-token
class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write(f'{color.RED}error{color.ENDCOLOR}: {color.YELLOW}%s{color.ENDCOLOR}\n\n' % message)
        self.print_help()
        sys.exit(2) 

def get_token():
    try:
        with open(token_file) as f:
            token = f.read().strip()
        f.close()
        if token:
            return token
    except FileNotFoundError:
        pass
    try:
        token = os.environ['TOKEN']
        if token:
            return token
    except:
        return None
token = get_token()

def list_vlans():
    show_vlan = 'https://api.linode.com/v4beta/networking/vlans'

    r = requests.get(show_vlan, auth=BearerAuth(token))
    resp = json.loads(r.text)

    linodes = []
    colwidth = []
    table_header = ["Created", "Vlan", "Region", "Linodes"]
    table_data = []

    for l in resp['data']:
        linodes.append(l['linodes'])

    list_len = len(linodes)
    converted_linodes = [[] for i in range(list_len)]

    for n, linode in enumerate(linodes):
        for l in linode:
            converted_linodes[n].append(str(l))

    for n, linode in enumerate(resp['data']):
        table_data.append([ linode['created'], linode['label'], linode['region'], ' '.join(converted_linodes[n]) ])
    print(tabulate(table_data, table_header, tablefmt="fancy_grid", maxcolwidths=[None, None, None, 8] ))
        
def view_vlan(vlan):
    show_vlan = 'https://api.linode.com/v4beta/networking/vlans'
    r = requests.get(show_vlan, auth=BearerAuth(token))
    resp = json.loads(r.text)

    linodes = []
    table_header = ["ID", "Linode", "IPAM Address"]
    table_data = []

    for l in resp['data']:
        if l['label'] == vlan:
            linodes.append(l['linodes'])
            break
    if len(linodes) == 0:
        print(f'{color.RED}Error{color.ENDCOLOR}: VLAN {color.BOLD}"{vlan}"{color.ENDCOLOR} was NOT found!')
        exit(1)

    for n, linode in enumerate(linodes[0]):
        linode_label = f'https://api.linode.com/v4/linode/instances/{linode}'
        linode_vlan = f'https://api.linode.com/v4/linode/instances/{linode}/configs'
        req_vlan = requests.get(linode_vlan, auth=BearerAuth(token)) 
        req_label = requests.get(linode_label, auth=BearerAuth(token))
        resp_vlan = json.loads(req_vlan.text)
        resp_label = json.loads(req_label.text)

        for linode in resp_vlan['data'][0]['interfaces']:
            if linode['label'] == vlan:
                table_data.append([ str(resp_label['id']), resp_label['label'], linode['ipam_address'] ])
           
    print(f"{color.GREEN}Vlan Name{color.ENDCOLOR}: {color.RED}{vlan}{color.ENDCOLOR}")
    print(tabulate(table_data, table_header, tablefmt="fancy_grid", maxcolwidths=[None, None, 18, None] ))       

def main():
    parser = MyParser()
    parser.add_argument('--list_vlans', action='store_true', required=False, help='list VLANs on account')
    parser.add_argument('--view_vlan', type=str, required=False, help='View the Linodes part of the supplied VLAN')
    args = parser.parse_args()

    # if no args provided
    if not args.list_vlans and not args.view_vlan:
        print(f"{color.RED}Error:{color.ENDCOLOR} {color.YELLOW}no arguments provided{color.ENDCOLOR}\n")
        parser.parse_args(['-h'])
        sys.exit(1)

    if args.list_vlans:
        list_vlans()
    if args.view_vlan:
        view_vlan(args.view_vlan)

if __name__ == '__main__':
    if token == None:
        print(f"{color.RED}Error:{color.ENDCOLOR} {color.YELLOW}No TOKEN found. Please export TOKEN or update the token file ({token_file}).{color.ENDCOLOR}")
        sys.exit(1)
    else:
        main()