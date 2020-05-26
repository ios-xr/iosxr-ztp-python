#!/usr/bin/env python

# Since /pkg/bin is not in default PYTHONPATH, the following 
# two lines are necessary to be able to use the ztp_helper.py
# library on the box

import sys
sys.path.append("/pkg/bin/")

import json, tempfile
from pprint import pprint
import os, subprocess, shutil
from ztp_helper import ZtpHelpers

ROOT_LR_USER = "netops"
ROOT_USER_CREDENTIALS = "$1$7kTu$zjrgqbgW08vEXsYzUycXw1"
EXPECTED_VERSION = "7.1.1.108I"
#EXPECTED_VERSION = "6.6.3.19I"

class ZtpFunctions(ZtpHelpers):

    def set_root_user(self):
        """User defined method in Child Class
           Sets the root user for IOS-XR during ZTP
           Leverages xrapply() method in ZtpHelpers Class.
           :return: Return a dictionary with status and output
                    { 'status': 'error/success', 'output': 'output from xrapply' }
           :rtype: dict
        """
        config = """ !
                     username %s 
                     group root-lr
                     group cisco-support
                     secret 5 %s 
                     !
                     end""" % (ROOT_LR_USER, ROOT_USER_CREDENTIALS)



        with tempfile.NamedTemporaryFile(delete=True) as f:
            f.write("%s" % config)
            f.flush()
            f.seek(0)
            result = self.xrapply(f.name)

        if result["status"] == "error":

            self.syslogger.info("Failed to apply root user to system %s"+json.dumps(result))

        return result

    def admincmd(self, cmd=None):
        """Issue an admin exec cmd and obtain the output
           :param cmd: Dictionary representing the XR exec cmd
                       and response to potential prompts
                       { 'exec_cmd': '', 'prompt_response': '' }
           :type cmd: string 
           :return: Return a dictionary with status and output
                    { 'status': 'error/success', 'output': '' }
           :rtype: string
        """

        if cmd is None:
            return {"status" : "error", "output" : "No command specified"}

        status = "success"


        if not isinstance(cmd, dict):
            return {
                "status":
                "error",
                "output":
                "Dictionary expected as cmd argument, see method documentation"
            }

        status = "success"

        if "prompt_response" not in cmd:
            cmd["prompt_response"] = ""

        if self.debug:
            self.logger.debug(
                "Received admin exec command request: \"%s\"" % cmd["exec_cmd"])
            self.logger.debug("Response to any expected prompt \"%s\"" %
                              cmd["prompt_response"])


        cmd = "export AAA_USER="+self.root_lr_user+" && source /pkg/bin/ztp_helper.sh && echo -ne \""+cmd["exec_cmd"]+ cmd["prompt_response"]+"\\n \" | xrcmd \"admin\""

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        out, err = process.communicate()


        if process.returncode:
            status = "error"
            output = "Failed to get command output"
        else:
            output_list = []
            output = ""

            for line in out.splitlines():
                fixed_line= line.replace("\n", " ").strip()
                output_list.append(fixed_line)
                if "syntax error: expecting" in fixed_line:
                    status = "error"
                output = filter(None, output_list)    # Removing empty items

        if self.debug:
            self.logger.debug("Exec command output is %s" % output)

        return {"status" : status, "output" : output}




if __name__ == "__main__":

    # Create an Object of the child class, syslog parameters are optional. 
    # If nothing is specified, then logging will happen to local log rotated file.

    ztp_script = ZtpFunctions(syslog_server="192.168.152.2", syslog_port=514)

    ztp_script.syslogger.info("###### Starting ZTP RUN on NCS5500 ######")

    # Enable verbose debugging to stdout/console. By default it is off
    ztp_script.toggle_debug(1)

    # Change context to XR VRF in the linux shell when needed. Depends on when user changes config to create network namespace.

    # No Config applied yet, so start with global-vrf(default)"
    ztp_script.set_vrf("global-vrf")


    # Create root user, required for executing Admin commands
    user_setup = ztp_script.set_root_user()

    if user_setup["status"] == "success":
        ztp_script.root_lr_user = ROOT_LR_USER
    else:
        ztp_script.syslogger.info("Failed to create root_lr_user, aborting....")
        sys.exit(1)

    # Check current version running on the system
    show_version = ztp_script.xrcmd({"exec_cmd" : "show version"})

    version = show_version["output"][7].split(":")[1].strip() 

    if version == EXPECTED_VERSION:
        ztp_script.syslogger.info("Expected Version "+str(EXPECTED_VERSION)+" is running, continue and do other tasks")
       
        # Do other tasks here....
        
        # Exit cleanly upon completion
        sys.exit(0)

    else:
        # If choosing to change Release using iPXE, reboot box to iPXE mode here
        # After the box does iPXE it will rerun ZTP, if the image version is correct the second time
        # then "if" condition above is true and ZTP script will continue doing other things.

        # Reload box to iPXE

        #ipxe_reboot = ztp_script.admincmd({"exec_cmd" : "hw-module location all bootmedia network reload",
        #                                   "prompt_response" : "yes\n"
        #                                 })
        ipxe_reboot = ztp_script.admincmd({"exec_cmd" : "show platform"})

        if ipxe_reboot["status"] == "error":
            ztp_script.syslogger.info("Failed to reboot box to iPXE, erroring out")
            sys.exit(1)
        else:
            ztp_script.syslogger.info("Box already rebooting by now, so this message might not go out")
           
