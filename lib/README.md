## IOS-XR ZTP python library:

This library is available on the router by default starting IOS-XR 6.2.2  

The python library is provided in the github repository to help a user easily understand the structure of the library
and then inherit in the user side ztp script.

This file will exist at the location:  /pkg/bin/ztp_helper.py  on your router.

To utilize the python library and/or inherit in user defined classes, make sure your syspath includes /pkg/bin as 
shown below:  

```
import sys
sys.path.append("/pkg/bin/")
from ztp_helper import ZtpHelpers

```

You will find sample scripts to get you started at the root of this github repository.
Specifically:

*  **sample_ztp_script.py** : This is a sample ZTP script that creates an inherited class and runs some sample commands to show how XR CLI commands, syslog, error checking would work.

*  **exhaustive_ztp_script.py** :  This is a much more exhaustive script. It actually solves a ZTP use case where the mgmt port is placed in a VRF, we enable moving across network namespaces, set up cron jobs, work with active/standby RPs etc. Use this script to leverage some code pieces in your own script, if needed.
