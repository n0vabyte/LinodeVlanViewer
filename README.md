# Linode VLAN Viewer
# About

If you are using the Akamai Cloud to host your workload on virtualized instances we call Linodes, most likely you are aware of some the tools the platform offers. One of which is the [Linode CLI ](https://www.linode.com/products/cli/).


The purpose of this extremely small repo is to solve (more of a stop gap) the limitations of the API when it comes to [Linode VLANs](https://www.linode.com/products/vlan/). The product itself is great, however the API endoint is only limited to viewing VLANs on the account. The [vlans.py](https://github.com/n0vabyte/LinodeVlanViewer/blob/main/script/vlans.py) script will allow you to iterate through the instances that are part of a VLAN to get their respective IPAM address.

Curretly, the CLI will only allow you to view the LinodeIDs but keeps you guessing on what the IPAM addresses are:
![](/images/vlanls.png)

# How To Use

1. Install requirements

The very first thing that you need to do is install the requirements.txt file. We are going to be using a library called `tabulate` to provide a similar experience the Linode CLI.

```
pip3 install -r requirements.txt
```

2. Export the token

Next, you will need a Linode API token to use the script. The script will tell you if run it without a token variable as well. If you don't have a token, go ahead and get that sorted out first:

- https://www.linode.com/docs/products/tools/api/get-started/#get-an-access-token

Now export the token on your shell with your own value:

```
export TOKEN=ASDF255FFGK_REPLACE_ME_594JFSDKJFKJFJ467J
```

Another option available is to put the token in `/tmp/token`.

3. Run the script

If you run the script without any arguements, the help function will show up. 

```
Error: no arguments provided

usage: linode_vlans.py [-h] [--list_vlans] [--view_vlan VIEW_VLAN]

optional arguments:
  -h, --help            show this help message and exit
  --list_vlans          list VLANs on account
  --view_vlan VIEW_VLAN
                        View the Linodes part of the supplied VLAN
```

The script is pretty simple with 2 arguements:

- `--list_vlans`:

Shows the same information as the Linode CLI. It display all of the VLANs on the account and the Linode IDs associated with the VLAN.

- `--view_vlan $VLAN_NAME`:

Unlike the Linode CLI, this allows you to see the Linode label and the actual IPAM address assigned to the Linode. For example, I have a `test` VLAN for demonstration:

![](/images/viewvlan.png)

# Limitations

As with everything, there are limitations. The performance of the script varies depending on the size of the VLAN because we have to iterate through two API endpoints:

- https://api.linode.com/v4/linode/instances
- https://api.linode.com/v4/linode/instances/$LINODE_ID/configs

**For *every* Linode**. So basic math: If we have a VLAN with 100 Linodes and it takes .500 seconds to get and sort the data from both endpoints..You get it the point :) Hence the script is network-bound and will vary in response time.

The reason why we need to hit both endpoints is because the Linode label and ID are in the first endpoint and the VLAN/IPMA information is stored in the configuration profile for the Linode.