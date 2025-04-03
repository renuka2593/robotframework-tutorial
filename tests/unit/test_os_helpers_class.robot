*** Settings ***
Documentation     Test cases for OS helpers functionality using the class-based approach
Library           ../../resources/libraries/OSHelpers.py
Library           Collections

*** Test Cases ***
Verify OS Helper Functions
    [Documentation]    Verify that OS helper functions return expected data types
    
    # Get and verify hostname
    ${hostname}=    Get Hostname
    Should Not Be Empty    ${hostname}
    Log    Hostname: ${hostname}
    
    # Get and verify IP address
    ${ip}=    Get IP Address
    Should Match Regexp    ${ip}    ^\\d+\\.\\d+\\.\\d+\\.\\d+$
    Log    IP Address: ${ip}
    
    # Get and verify MAC address
    ${mac}=    Get MAC Address
    Should Match Regexp    ${mac}    ^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$
    Log    MAC Address: ${mac}
    
    # Get and verify OS info
    ${os_info}=    Get OS Info
    Dictionary Should Contain Key    ${os_info}    system
    Dictionary Should Contain Key    ${os_info}    version
    Dictionary Should Contain Key    ${os_info}    architecture
    Log    OS: ${os_info}[system] ${os_info}[release]
    
    # Get and verify username
    ${username}=    Get Username
    Should Not Be Empty    ${username}
    Log    Username: ${username}
    
    # Log all system information
    Log System Information

Verify CPU And Memory Information
    [Documentation]    Verify CPU and memory information
    
    # Get and verify CPU info
    ${cpu_info}=    Get CPU Info
    Dictionary Should Contain Key    ${cpu_info}    physical_cores
    Dictionary Should Contain Key    ${cpu_info}    total_cores
    Dictionary Should Contain Key    ${cpu_info}    cpu_usage
    Should Be True    ${cpu_info}[physical_cores] > 0
    Should Be True    ${cpu_info}[total_cores] >= ${cpu_info}[physical_cores]
    Log    CPU Cores: ${cpu_info}[physical_cores] physical, ${cpu_info}[total_cores] total
    Log    CPU Usage: ${cpu_info}[cpu_usage]%
    
    # Get and verify memory info
    ${memory_info}=    Get Memory Info
    Dictionary Should Contain Key    ${memory_info}    total
    Dictionary Should Contain Key    ${memory_info}    available
    Dictionary Should Contain Key    ${memory_info}    used
    Should Be True    ${memory_info}[total] > 0
    Should Be True    ${memory_info}[available] <= ${memory_info}[total]
    Log    Memory: ${memory_info}[total] GB total, ${memory_info}[available] GB available

Verify Disk Information
    [Documentation]    Verify disk information
    
    ${disk_info}=    Get Disk Info
    Should Not Be Empty    ${disk_info}
    Log    Found ${disk_info.__len__()} disk partitions
    
    # Verify first partition info
    ${first_partition}=    Set Variable    ${disk_info}[0]
    Dictionary Should Contain Key    ${first_partition}    device
    Dictionary Should Contain Key    ${first_partition}    mountpoint
    Dictionary Should Contain Key    ${first_partition}    total_size_gb
    Log    First partition: ${first_partition}[device] mounted at ${first_partition}[mountpoint]
    Log    Size: ${first_partition}[total_size_gb] GB total, ${first_partition}[free_gb] GB free

Verify Network Information
    [Documentation]    Verify network interface information
    
    ${network_info}=    Get Network Info
    Should Not Be Empty    ${network_info}
    Log    Found ${network_info.__len__()} network interfaces
    
    # Verify first interface info
    ${first_interface}=    Set Variable    ${network_info}[0]
    Dictionary Should Contain Key    ${first_interface}    interface
    Dictionary Should Contain Key    ${first_interface}    mac_address
    Dictionary Should Contain Key    ${first_interface}    ipv4_addresses
    Log    Interface: ${first_interface}[interface]
    Log    MAC: ${first_interface}[mac_address] 