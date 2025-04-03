#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utility functions for OS specific operations.
"""

import os
import socket
import platform
import uuid
import psutil
import getpass
from typing import List, Dict, Union


def get_hostname() -> str:
    """Get the hostname of the current machine."""
    return socket.gethostname()


def get_fqdn() -> str:
    """Get the fully qualified domain name of the current machine."""
    return socket.getfqdn()


def get_ip_address() -> str:
    """Get the primary IP address of the current machine."""
    try:
        # Create a socket to determine primary IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't need to be reachable
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'


def get_mac_address() -> str:
    """Get the MAC address of the primary network interface."""
    return ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                    for elements in range(0, 8*6, 8)][::-1])


def get_os_info() -> Dict[str, str]:
    """Get operating system information."""
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'architecture': platform.machine(),
        'processor': platform.processor()
    }


def get_username() -> str:
    """Get the current logged-in username."""
    return getpass.getuser()


def get_cpu_info() -> Dict[str, Union[int, float, str]]:
    """Get CPU information."""
    cpu_info = {
        'physical_cores': psutil.cpu_count(logical=False),
        'total_cores': psutil.cpu_count(logical=True),
        'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else 0,
        'current_frequency': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
        'cpu_usage': psutil.cpu_percent()
    }
    return cpu_info


def get_memory_info() -> Dict[str, Union[int, float]]:
    """Get memory information in GB."""
    mem = psutil.virtual_memory()
    return {
        'total': round(mem.total / (1024**3), 2),  # GB
        'available': round(mem.available / (1024**3), 2),  # GB
        'used': round(mem.used / (1024**3), 2),  # GB
        'percent_used': mem.percent
    }


def get_disk_info() -> List[Dict[str, Union[str, int, float]]]:
    """Get disk usage information for all partitions."""
    partitions = []
    for partition in psutil.disk_partitions(all=False):
        if os.name == 'nt' and ('cdrom' in partition.opts or partition.fstype == ''):
            # Skip CD-ROM drives on Windows
            continue
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            partitions.append({
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'fstype': partition.fstype,
                'total_size_gb': round(usage.total / (1024**3), 2),
                'used_gb': round(usage.used / (1024**3), 2),
                'free_gb': round(usage.free / (1024**3), 2),
                'percent_used': usage.percent
            })
        except PermissionError:
            continue
    return partitions


def get_network_info() -> List[Dict[str, Union[str, List[str]]]]:
    """Get information about network interfaces."""
    network_info = []
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        addresses = {'ipv4': [], 'ipv6': [], 'mac': None}
        
        for address in interface_addresses:
            if address.family == socket.AF_INET:
                addresses['ipv4'].append(address.address)
            elif address.family == socket.AF_INET6:
                addresses['ipv6'].append(address.address)
            elif address.family == psutil.AF_LINK:
                addresses['mac'] = address.address
        
        network_info.append({
            'interface': interface_name,
            'mac_address': addresses['mac'],
            'ipv4_addresses': addresses['ipv4'],
            'ipv6_addresses': addresses['ipv6']
        })
    return network_info 