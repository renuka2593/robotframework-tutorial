# Windows Application Installation Helpers

This module provides utilities for automating the installation and uninstallation of Windows desktop applications using pywinauto and FlaUI.

## Features

- Silent and interactive installation of Windows applications (.exe, .msi, .appx)
- Handling common installation dialogs (Next, License Agreement, Installation Location, Finish)
- Uninstallation through direct uninstaller or Control Panel
- Support for both pywinauto (Python-based) and FlaUI (.NET-based) automation frameworks

## Prerequisites

### For pywinauto:

- Python 3.7+
- pywinauto 0.6.8+
- psutil 5.9.0+

### For FlaUI (optional):

- Python 3.7+
- pythonnet 3.0.1+
- FlaUI installed on the system
- .NET Framework or .NET Core

## Installation

```bash
pip install -r requirements.txt
```

## Usage in Robot Framework

```robot
*** Settings ***
Resource    resources/install_helpers.resource
Library     OperatingSystem

*** Test Cases ***
Install Application Example
    # Install using EXE installer silently
    ${result}=    Install EXE Application
    ...    exe_path=C:\\path\\to\\installer.exe
    ...    silent=${TRUE}
    ...    timeout=120

    # Verify installation
    Should Be True    ${result}
    File Should Exist    C:\\Program Files\\MyApp\\MyApp.exe
```

## Available Keywords

### PyWinAuto-based Keywords

- `Install Application With PyWinAuto` - Install an application using PyWinAuto
- `Uninstall Application With PyWinAuto` - Uninstall an application using PyWinAuto
- `Run Silent Installation With PyWinAuto` - Run a silent installation
- `Install MSI Application` - Install an MSI application silently
- `Install EXE Application` - Install an EXE application (silent or interactive)
- `Check If Process Is Running` - Check if a process is running
- `Wait For Window To Appear` - Wait for a window to appear

### FlaUI-based Keywords (Placeholder - Requires Implementation)

- `Install Application With FlaUI` - Install an application using FlaUI
- `Uninstall Application With FlaUI` - Uninstall an application using FlaUI

## Examples

### Silent Installation of MSI

```robot
${result}=    Install MSI Application
...    msi_path=C:\\path\\to\\app.msi
...    properties=INSTALLDIR="C:\\Custom Path" ACCEPT_EULA=1
```

### Interactive Installation with Custom Path

```robot
${result}=    Install Application With PyWinAuto
...    installer_path=C:\\path\\to\\setup.exe
...    silent=${FALSE}
...    custom_install_path=D:\\Apps\\MyApplication
```

### Uninstallation

```robot
${result}=    Uninstall Application With PyWinAuto
...    app_name=My Application
...    silent=${TRUE}
```

## Implementing FlaUI Support

To implement FlaUI support:

1. Install FlaUI on your system
2. Install pythonnet (`pip install pythonnet`)
3. Modify the FlaUI placeholder functions in `utils/installation_helpers.py`

Example implementation outline:

```python
import clr
import sys

# Add FlaUI assemblies
sys.path.append("path/to/FlaUI/dlls")
clr.AddReference("FlaUI.Core")
clr.AddReference("FlaUI.UIA3")

# Now you can import FlaUI classes
from FlaUI.Core.AutomationElements import *
from FlaUI.UIA3 import *
```

## Known Limitations

- Silent installation arguments vary widely between different installers
- Some applications may have non-standard installation dialogs requiring custom handling
- FlaUI implementation requires additional setup and configuration
