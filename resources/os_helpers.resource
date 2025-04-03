*** Settings ***
Documentation     OS Helper keywords for Robot Framework tests
Library           ${CURDIR}/../utils/os_helpers.py

*** Keywords ***
Get System Hostname
    [Documentation]    Get the hostname of the current machine
    ${hostname}=    Get Hostname
    [Return]    ${hostname}

Get System FQDN
    [Documentation]    Get the fully qualified domain name of the current machine
    ${fqdn}=    Get FQDN
    [Return]    ${fqdn}

Get System IP Address
    [Documentation]    Get the primary IP address of the current machine
    ${ip}=    Get IP Address
    [Return]    ${ip}

Get System MAC Address
    [Documentation]    Get the MAC address of the primary network interface
    ${mac}=    Get MAC Address
    [Return]    ${mac}

Get Operating System Info
    [Documentation]    Get operating system information as a dictionary
    ${os_info}=    Get OS Info
    [Return]    ${os_info}

Get Current Username
    [Documentation]    Get the current logged-in username
    ${username}=    Get Username
    [Return]    ${username}

Get CPU Information
    [Documentation]    Get CPU information as a dictionary
    ${cpu_info}=    Get CPU Info
    [Return]    ${cpu_info}

Get Memory Information
    [Documentation]    Get memory information as a dictionary (in GB)
    ${memory_info}=    Get Memory Info
    [Return]    ${memory_info}

Get Disk Information
    [Documentation]    Get disk usage information for all partitions
    ${disk_info}=    Get Disk Info
    [Return]    ${disk_info}

Get Network Information
    [Documentation]    Get information about network interfaces
    ${network_info}=    Get Network Info
    [Return]    ${network_info}

Log System Information
    [Documentation]    Log all system information for debugging purposes
    ${hostname}=       Get System Hostname
    ${ip}=             Get System IP Address
    ${os_info}=        Get Operating System Info
    ${username}=       Get Current Username
    ${cpu_info}=       Get CPU Information
    ${memory_info}=    Get Memory Information
    
    Log    Hostname: ${hostname}
    Log    IP Address: ${ip}
    Log    OS: ${os_info}[system] ${os_info}[release] (${os_info}[version])
    Log    Architecture: ${os_info}[architecture]
    Log    Username: ${username}
    Log    CPU: ${cpu_info}[physical_cores] physical cores, ${cpu_info}[total_cores] total cores
    Log    Memory: ${memory_info}[total] GB total, ${memory_info}[available] GB available 