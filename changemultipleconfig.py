import concurrent.futures
import sys
import argparse
import time
import getpass
import os

platform = 'juniper'
username = input("Username?: ")
password = getpass.getpass(prompt="Password?: ")
devicelist = input("File containing list of network devices? (hosts.txt contains all Juniper devices if you'd like to search all): ")
command = input("Config to change? (line 1): ")
command1 = input("Config to change? (line 2): ")
command2 = input("Config to change? (line 3): ")
command3 = input("Config to change? (line 4): ")
outputtxt = input("Output file name? (filename of your choosing - this outputs to /home/python/output/): ")
outputinbetween = os.path.join("/home/python/output/", outputtxt)
outputwrite = open(outputinbetween, 'w', os.O_NONBLOCK)


try:
    from netmiko import ConnectHandler

except ImportError:
    print('Please install netmiko module: pip3 install netmiko')
    raise

except:
    print('Unexpected error:', sys.exc_info()[0])
    raise

def process(devices):
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        hostname = {executor.submit(gethostname, device): device for device in devices}
        for future in concurrent.futures.as_completed(hostname):
            device = hostname[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (device, exc))
            else:
                print('[{}] {}'.format(device, data))
                outputwrite.write('Device hostname: {} {}'.format(device, data))



def lcount(keyword, fname):
  with open(fname, 'r') as fin:
    return sum([1 for line in fin if keyword in line])

def gethostname(device):
    dev = {
        'device_type': platform,
        'ip': device,
        'username': username,
        'secret': password,
        'password': password,
        'global_delay_factor': 4,
        'verbose': True,
    }

    device = ConnectHandler(**dev)
    device.enable()
    device_commands = [ command,
                        command1,
                        command2,
                        command3,
                        'commit']
    hostname = device.send_config_set(device_commands)
    return hostname

if __name__ == '__main__':
    devices = open(devicelist)
    start = time.time()
    process(devices)
    outputwrite.close()
    print('Time taken = {0:.5f}'.format(time.time() - start))
    print("%d devices opened" % len(open(devicelist).readlines()))
    open(outputinbetween).readlines()
    print("%d devices successfully accessed" % lcount('commit confirmed', outputinbetween))
