#!/usr/bin/env python

# Since /pkg/bin is not in default PYTHONPATH, the following 
# two lines are necessary to be able to use the ztp_helper.py
# library on the box

# This script is used to check the current version of the image on the box
# and if it matches the expected version an install commit is issued for any 
# prior upgrades followed by user defined steps.
# If the current version does not match the expected version, then a fresh
# ISO is installed from a known URL and XR install add/activate is used to
# upgrade/downgrade to the specified ISO



import sys
sys.path.append("/pkg/bin/")

import json, tempfile
from pprint import pprint
import os, subprocess, shutil
from ztp_helper import ZtpHelpers
import re, time
from time import gmtime, strftime
import signal 

ROOT_LR_USER = "netops"
ROOT_USER_CREDENTIALS = "$1$7kTu$zjrgqbgW08vEXsYzUycXw1"
SERVER_URL = "http://192.168.152.2:9090/"

#EXPECTED_VERSION = "7.1.1.108I"
#ISO_URL = SERVER_URL + "ncs5500-711/ncs5500-goldenk9-x-7.1.1.108I-0.iso"

EXPECTED_VERSION = "6.6.3.19I"
ISO_URL = SERVER_URL + "663-19I/ncs5500-fullk9-x.iso"



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


    def commit_replace_empty(self):
        config = """ !
                     hostname ios
                     !
                     end"""



        with tempfile.NamedTemporaryFile(delete=True) as f:
            f.write("%s" % config)
            f.flush()
            f.seek(0)
            result = self.xrreplace(f.name)

        if result["status"] == "error":

            self.syslogger.info("Failed to wipe out configuration: "+json.dumps(result))

        return result




    def install_xr_add_activate_iso(self, iso_url, routine_upgrade=True):
        """ Method to upgrade/downgrade XR ISO through initial download followed
            by local install and cleanup
 
            Uses install add+activate utilities
            :param iso_url: Complete URL of the iso to be downloaded
                                and installed
            :type iso_url: str
            :param routine_upgrade: Flag to wipe out config before activating ISO (False)
                                    or directly activate without touching config (True)
            :type boolean
            :return: Dictionary specifying success/error and an associated message
                     {'status': 'success/error',
                      'output': 'success/error message',
                      'warning': 'warning if cleanup fails'}
            :rtype: dict
        """

        result = {"status": "error", "output" : "Installation of package  failed!"}

        # First download the package to the /misc/app_host/scratch folder

        output = self.download_file(iso_url, destination_folder="/misc/disk1")

        if output["status"] == "error":
            if self.debug:
                self.logger.debug("Package Download failed, aborting installation process")
            self.syslogger.info("Package Download failed, aborting installation process")

            return result

        elif output["status"] == "success":
            if self.debug:
                self.logger.debug("Package Download complete, starting installation process")

            self.syslogger.info("Package Download complete, starting installation process")

            iso_name = output["filename"]
            iso_location = output["folder"]
            iso_path = os.path.join(iso_location, iso_name)

            # Run the install add command in XR exec 

            install_add = self.xrcmd({"exec_cmd" : "install add source harddisk: %s" % (iso_name)})

            if install_add["status"] == "success":
                result_install_add = re.search("Install operation [+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)? started by", install_add["output"][0]) 
                if result_install_add:
                    install_add_id = result_install_add.group(1)
                else:
                    self.logger.debug("Failed to determine Install add id, aborting")
                    result["status"] = "error"
                    result["output"] = "Failed to detemine install add id, aborting"
                    return result

                install_add_result = "error"
                t_end = time.time() + 60 * 5
                while time.time() < t_end: 
                            
                    install_log = self.xrcmd({"exec_cmd" : "show install log "+str(install_add_id)})
                            
                    if install_log["status"] == "error":
                            result["status"] = "error"
                            result["output"] = "Failed to fetch output of show install log -Installation of iso %s failed" % iso_name
                            # Cleanup
                            try:
                                os.remove(iso_path)
                            except OSError:
                                result["warning"] = "failed to remove iso from path: "+str(iso_path)
                        
                            return result
                    else:
                        if "Ending operation "+str(install_add_id) in install_log["output"][-1]:
                            if "Install operation "+str(install_add_id)+" finished successfully" in install_log["output"][-2]:
                                self.logger.debug("Install add successful, ready to activate iso %s" % (iso_name))
                            install_add_result = "success" 
                            break 
                        else:
                            # Sleep for 10 seconds before checking again
                            time.sleep(10)
                            if self.debug:
                                self.logger.debug("Waiting for install add of %s iso to complete" % iso_name)
                            self.syslogger.info("Waiting for install add of  %s iso to complete" % iso_name)


                if install_add_result == "error":
                    result["status"] = "error"
                    result["output"] =  "Install add of %s iso timed out" % iso_name
                    # Cleanup
                    try:
                        os.remove(iso_path)
                    except OSError:
                        result["warning"] = "failed to remove iso from path: "+str(iso_path)
                    return result


            else:
                result["status"] = "error"
                result["output"] = "Failed to execute install add command for iso: %s" % iso_name
                # Cleanup
                try:
                    os.remove(iso_path)
                except OSError:
                    result["warning"] = "failed to remove iso from path: "+str(iso_path)
                return result


            # To trigger ZTP post upgrade, must do a commit replace before activating
            if not routine_upgrade:
                commit_replace = self.commit_replace_empty()
                if commit_replace["status"] == "error":
                    self.syslogger.info("Aborting install activate of iso, failed to wipe out config...")
                    result["status"] = "error"
                    result["output"] = "Aborting install activate of iso, failed to wipe out config"
                    # Cleanup
                    try:
                        os.remove(iso_path)
                    except OSError:
                        result["warning"] = "failed to remove iso from path: "+str(iso_path)
                    return result
                ##else:
                #   ztp_clean = self.xrcmd({"exec_cmd" : "ztp clean noprompt"})
                #    if ztp_clean["status"] == "error":
                #        self.syslogger.info("Aborting install activate of iso, failed to clean ZTP state...")
                #        result["status"] = "error"
                #        result["output"] = "Aborting install activate of iso, failed to clean ZTP state"
                #        # Cleanup
                #        try:
                #           os.remove(iso_path)
                #        except OSError:
                #            result["warning"] = "failed to remove iso from path: "+str(iso_path)
                #        return result

                     

            # Now activate the iso

            install_activate = self.xrcmd({"exec_cmd" : "install activate id %s noprompt" % (install_add_id)})


            if install_activate["status"] == "success":
                result_install_activate = re.search("Install operation [+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)? started by", install_activate["output"][0])
                if result_install_activate:
                    install_activate_id = result_install_activate.group(1)
                else:
                    self.logger.debug("Failed to determine Install activate id, aborting")
                    result["status"] = "error"
                    result["output"] = "Failed to detemine install activate id, aborting"
                    return result


                t_end = time.time() + 60 * 5
                while time.time() < t_end:

                    install_log = self.xrcmd({"exec_cmd" : "show install log "+str(install_activate_id)})

                    if install_log["status"] == "error":
                            result["status"] = "error"
                            result["output"] = "Failed to fetch output of show install log -Installation of iso %s failed" % iso_name
                            # Cleanup
                            try:
                                os.remove(iso_path)
                            except OSError:
                                result["warning"] = "failed to remove iso from path: "+str(iso_path)

                            return result
                    else:
                        if "Ending operation "+str(install_activate_id) in install_log["output"][-1]:
                            if "Install operation "+str(install_activate_id)+" finished successfully" in install_log["output"][-2]:
                                self.logger.debug("Install activate successful, node should reload any moment")
                            result["status"] = "success"
                            result["output"] = "Install activate successful, node should reload any moment" 
                            break
                        else:
                            # Sleep for 10 seconds before checking again
                            time.sleep(10)
                            if self.debug:
                                self.logger.debug("Waiting for install activate of %s iso to complete" % iso_name)
                            self.syslogger.info("Waiting for install activate of  %s iso to complete" % iso_name)

                if result["status"] == "error":
                    result["output"] =  "Installation of %s iso timed out" % iso_name
                    # Cleanup
                    try:
                        os.remove(iso_path)
                    except OSError:
                        result["warning"] = "failed to remove iso from path: "+str(iso_path)


                return result
            else:
                result["status"] = "error"
                result["output"] = "Failed to execute install activate command for iso: %s" % iso_name
                # Cleanup
                try:
                    os.remove(iso_path)
                except OSError:
                    result["warning"] = "failed to remove iso from path: "+str(iso_path)
                return result
                                   
            


    def xr_install_commit(self, duration=60):
        """User defined method in Child Class
           Issues an "install commit" to make XR packages persistent. 
           This ensures packages remain active post reloads. 
           Leverages xrcmd() method in ZtpHelpers Class.
           Should be executed post call to install_xr_package() from ZtpHelpers.
           Returns error if 'duration' is exceeded during "show install committed"
           check.
           :param duration: Duration for which the script must wait for the active 
                            packages to be committed. 
           :type duration: int
 
           :return: Return a dictionary with status 
                    { 'status': 'error/success' }
           :rtype: dict
        """
        install_commit = self.xrcmd({"exec_cmd" : "install commit"})

        if install_commit["status"] == "error":
            self.syslogger.info("Failed to commit installed packages")
            return {"status" : "error"} 
        else:
            commit_success = False
            t_end = time.time() + duration
            while time.time() < t_end:
                # Check that the install commit was successful
                commit_state = self.xrcmd({"exec_cmd" : "show install committed"})

                if commit_state["status"] == "error":
                    self.syslogger.info("show install committed failed to execute ")
                    return {"status" : "error"} 

                active_state = self.xrcmd({"exec_cmd" : "show install active"})
                if active_state["status"] == "error":
                    self.syslogger.info("show install active failed to execute ")
                    return {"status" : "error"} 

                # Excluding the date (first line) and lines saying Active vs Committed,
                #  the rest of the commit and active state outputs must match

                commit_output = commit_state["output"][1:]
                commit_compare = [x for x in commit_output if "Committed" not in x]

                active_output = active_state["output"][1:]
                active_compare = [x for x in active_output if "Active" not in x]

                if ''.join(commit_compare) == ''.join(active_compare):
                    self.syslogger.info("Install commit successful!")
                    return {"status" : "success"}
                else:
                    self.syslogger.info("Install commit not done yet")
                    time.sleep(10)

            self.syslogger.info("Install commit unsuccessful!")
            return {"status" : "error"} 



def signal_handler(sig, frame):
    print('Terminating now..')
    sys.exit(0)


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
    ztp_script.syslogger.info("current version: "+version)
    ztp_script.syslogger.info("expected version: "+EXPECTED_VERSION)

    if version == EXPECTED_VERSION:
        ztp_script.syslogger.info("Expected Version "+str(EXPECTED_VERSION)+" is running, continue and do other tasks")
       
        # To make sure xr packages remain active post reloads, commit them
        ztp_script.syslogger.info("Committing the installed packages")
        install_commit = ztp_script.xr_install_commit(60)

        if install_commit["status"] == "error":
            ztp_script.syslogger.info("Failed to commit installed packages")
            sys.exit(1)
            # Do other tasks here....
        
            # Exit cleanly upon completion
        sys.exit(0)

    else:
        # Setting routine_upgrade to False. This will wipe out config ensuring ZTP runs again
        # post upgrade/downgrade. If set to True, it can be used to upgrade/downgrade software
        # as part of automation without running ZTP post reboot.
        result = ztp_script.install_xr_add_activate_iso(iso_url=ISO_URL, routine_upgrade=False)

        if result["status"] =="error":
            ztp_script.syslogger.info("Failed to install iso, error is : "+str(result["output"]))
            sys.exit(1)
        else:
            ztp_script.syslogger.info("Installed ISO successfully, node would reload now")    
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            signal.pause()
             
    

