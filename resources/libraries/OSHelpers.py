#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Robot Framework library for OS specific operations.
"""

import os
import socket
import platform
import uuid
import psutil
import getpass
from typing import List, Dict, Union
from robot.api.deco import keyword


class OSHelpers:
    """
    Library providing OS specific helper keywords for Robot Framework.
    Provides information about system, network, hardware, and more.
    """

    def __init__(self):
        """Initialize the OSHelpers library."""
        pass

    @keyword
    def get_hostname(self) -> str:
        """
        Get the hostname of the current machine.
        
        Returns:
            str: System hostname
            
        Example:
            | ${hostname}= | Get Hostname |
            | Log | System hostname is ${hostname} |
        """
        return socket.gethostname()

    @keyword
    def get_machine_name(self) -> str:
        """
        Get the machine name (computer name) of the current system.
        
        This returns the computer's network name (which might be different
        from the hostname in some environments).
        
        Returns:
            str: Machine name
            
        Example:
            | ${machine_name}= | Get Machine Name |
            | Log | Machine name is ${machine_name} |
        """
        return platform.node()

    @keyword
    def get_fqdn(self) -> str:
        """
        Get the fully qualified domain name of the current machine.
        
        Returns:
            str: Fully qualified domain name
            
        Example:
            | ${fqdn}= | Get FQDN |
            | Log | FQDN is ${fqdn} |
        """
        return socket.getfqdn()

    @keyword
    def get_ip_address(self) -> str:
        """
        Get the primary IP address of the current machine.
        
        Returns:
            str: Primary IP address
            
        Example:
            | ${ip}= | Get IP Address |
            | Log | Primary IP address is ${ip} |
        """
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

    @keyword
    def get_mac_address(self) -> str:
        """
        Get the MAC address of the primary network interface.
        
        Returns:
            str: MAC address
            
        Example:
            | ${mac}= | Get MAC Address |
            | Log | MAC address is ${mac} |
        """
        return ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                        for elements in range(0, 8*6, 8)][::-1])

    @keyword
    def get_os_info(self) -> Dict[str, str]:
        """
        Get operating system information.
        
        Returns:
            dict: Dictionary containing OS information with keys:
                - system: Operating system name
                - release: OS release information
                - version: OS version information
                - architecture: System architecture
                - processor: Processor information
                
        Example:
            | ${os_info}= | Get OS Info |
            | Log | Operating System: ${os_info}[system] ${os_info}[release] |
        """
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor()
        }

    @keyword
    def get_username(self) -> str:
        """
        Get the current logged-in username.
        
        Returns:
            str: Current username
            
        Example:
            | ${username}= | Get Username |
            | Log | Current user is ${username} |
        """
        return getpass.getuser()

    @keyword
    def get_cpu_info(self) -> Dict[str, Union[int, float, str]]:
        """
        Get CPU information.
        
        Returns:
            dict: Dictionary containing CPU information with keys:
                - physical_cores: Number of physical cores
                - total_cores: Total number of cores (including logical)
                - max_frequency: Maximum CPU frequency in MHz
                - current_frequency: Current CPU frequency in MHz
                - cpu_usage: Current CPU usage percentage
                
        Example:
            | ${cpu_info}= | Get CPU Info |
            | Log | CPU: ${cpu_info}[physical_cores] physical cores, ${cpu_info}[total_cores] total cores |
        """
        cpu_info = {
            'physical_cores': psutil.cpu_count(logical=False),
            'total_cores': psutil.cpu_count(logical=True),
            'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else 0,
            'current_frequency': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
            'cpu_usage': psutil.cpu_percent()
        }
        return cpu_info

    @keyword
    def get_memory_info(self) -> Dict[str, Union[int, float]]:
        """
        Get memory information in GB.
        
        Returns:
            dict: Dictionary containing memory information with keys:
                - total: Total memory in GB
                - available: Available memory in GB
                - used: Used memory in GB
                - percent_used: Percentage of memory used
                
        Example:
            | ${memory_info}= | Get Memory Info |
            | Log | Memory: ${memory_info}[total] GB total, ${memory_info}[available] GB available |
        """
        mem = psutil.virtual_memory()
        return {
            'total': round(mem.total / (1024**3), 2),  # GB
            'available': round(mem.available / (1024**3), 2),  # GB
            'used': round(mem.used / (1024**3), 2),  # GB
            'percent_used': mem.percent
        }

    @keyword
    def get_disk_info(self) -> List[Dict[str, Union[str, int, float]]]:
        """
        Get disk usage information for all partitions.
        
        Returns:
            list: List of dictionaries containing disk partition information with keys:
                - device: Device path
                - mountpoint: Mount point path
                - fstype: File system type
                - total_size_gb: Total size in GB
                - used_gb: Used space in GB
                - free_gb: Free space in GB
                - percent_used: Percentage of disk used
                
        Example:
            | ${disk_info}= | Get Disk Info |
            | Log | Found ${disk_info.__len__()} disk partitions |
            | FOR | ${partition} | IN | @{disk_info} |
            |     | Log | ${partition}[device]: ${partition}[free_gb] GB free of ${partition}[total_size_gb] GB |
            | END |
        """
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

    @keyword
    def get_network_info(self) -> List[Dict[str, Union[str, List[str]]]]:
        """
        Get information about network interfaces.
        
        Returns:
            list: List of dictionaries containing network interface information with keys:
                - interface: Interface name
                - mac_address: MAC address of the interface
                - ipv4_addresses: List of IPv4 addresses
                - ipv6_addresses: List of IPv6 addresses
                
        Example:
            | ${network_info}= | Get Network Info |
            | Log | Found ${network_info.__len__()} network interfaces |
            | FOR | ${interface} | IN | @{network_info} |
            |     | Log | ${interface}[interface]: ${interface}[mac_address] |
            | END |
        """
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

    @keyword
    def log_system_information(self):
        """
        Log all system information for debugging purposes.
        
        This keyword collects and logs information about the system,
        including hostname, IP, OS info, username, CPU, and memory.
        
        Example:
            | Log System Information |
        """
        hostname = self.get_hostname()
        ip = self.get_ip_address()
        os_info = self.get_os_info()
        username = self.get_username()
        cpu_info = self.get_cpu_info()
        memory_info = self.get_memory_info()
        
        print(f"Hostname: {hostname}")
        print(f"IP Address: {ip}")
        print(f"OS: {os_info['system']} {os_info['release']} ({os_info['version']})")
        print(f"Architecture: {os_info['architecture']}")
        print(f"Username: {username}")
        print(f"CPU: {cpu_info['physical_cores']} physical cores, {cpu_info['total_cores']} total cores")
        print(f"Memory: {memory_info['total']} GB total, {memory_info['available']} GB available") 