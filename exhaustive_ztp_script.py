#!/usr/bin/env python

# Since /pkg/bin is not in default PYTHONPATH, the following 
# two lines are necessary to be able to use the ztp_helper.py
# library on the box. You will need this library to access
# helpful APIs to work with XR CLI (xrcmd, xrapply, xrreplace)
# or netconf calls (xrnetconf - new in release 7.0.1)

import sys
sys.path.append("/pkg/bin/")
from ztp_helper import ZtpHelpers


import os, subprocess, shutil
import re, datetime, json, tempfile, time
from time import gmtime, strftime

ROOT_USER = "vagrant"
ROOT_USER_CREDENTIALS = "$1$FzMk$Y5G3Cv0H./q0fG.LGyIJS1" 
ROOT_USER_CLEARTEXT = "vagrant"
SERVER_URL = "http://11.11.11.2:9090/"
SERVER_URL_PACKAGES = SERVER_URL+"packages/"
SERVER_URL_SCRIPTS = SERVER_URL+"scripts/"
SERVER_URL_CONFIGS = SERVER_URL+"configs/"
CONFIG_FILE = "ncs5508_vrf_test.config"
K9SEC_PACKAGE = "ncs5500-k9sec-3.2.0.0-r6225.x86_64.rpm"
MGBL_PACKAGE = "ncs5500-mgbl-3.0.0.0-r6225.x86_64.rpm"
SYSLOG_SERVER = "11.11.11.2"
SYSLOG_PORT = 514
SYSLOG_LOCAL_FILE = "/root/ztp_python.log"
CRON_SCRIPT = "cron_action.py"

NODE_TYPE = ["Line Card",
             "LC",
             "Route Processor",
             "Route Switch Processor"]

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
                     end""" % (ROOT_USER, ROOT_USER_CREDENTIALS)



        with tempfile.NamedTemporaryFile(delete=True) as f:
            f.write("%s" % config)
            f.flush()
            f.seek(0)
            result = self.xrapply(f.name)

        if result["status"] == "error":

            self.syslogger.info("Failed to apply root user to system %s"+json.dumps(result))

        return result


    def all_nodes_ready(self):
        """ Method to check if all nodes on the chassis are ready 
            :return: Dictionary specifying success/error and an associated message
                     {'status': 'success/error',
                      'output':  True/False in case of success, 
                                 error mesage in case of error}
            :rtype: dict
        """

        show_inventory = self.xrcmd({"exec_cmd" : "show inventory | e PORT | i NAME:"})
        node_dict = {}

        if show_inventory["status"] == "success":
            try:
                for line in show_inventory["output"]:
                    if not any(tag in line for tag in ["NAME", "DESCR"]):
                        continue
                    str = '{'+line+'}'
                    str=str.replace("NAME", "\"NAME\"")
                    str=str.replace("DESCR", "\"DESCR\"")
                    if any(type in json.loads(str)['DESCR'] for type in NODE_TYPE):
                        node_dict[(json.loads(str)['NAME'])] = "inactive"
                        if self.debug:
                            self.logger.debug("Fetched Node inventory for the system")
                            self.logger.debug(node_dict)
            except Exception as e:
                if self.debug:
                    self.logger.debug("Error while fetching the node list from inventory")
                    self.logger.debug(e)
                return {"status": "error", "output": e }


            show_platform = self.xrcmd({"exec_cmd" : "show platform"})

            if show_platform["status"] == "success":
                try:
                    for node in node_dict:
                        for line in show_platform["output"]:
                            if node+'/CPU' in line.split()[0]:
                                node_state =  line.split()
                                xr_state = ' '.join(node_state[2:])
                                if 'IOS XR RUN' in xr_state:
                                    node_dict[node] = "active"
                except Exception as e:
                    if self.debug:
                        self.logger.debug("Error while fetching the XR status on node")
                        self.logger.debug(e)
                    return {"status": "error", "output": e }

            else:
                if self.debug:
                    self.logger.debug("Failed to get the output of show platform")
                return {"status": "error", "output": "Failed to get the output of show platform"}

        else:
            if self.debug:
                self.logger.debug("Failed to get the output of show inventory")
            return {"status": "error", "output": "Failed to get the output of show inventory"}


        if self.debug:
            self.logger.debug("Updated the IOS-XR state of each node")
            self.logger.debug(node_dict)

        if all(state == "active" for state in node_dict.values()):
            return {"status" : "success", "output": True}
        else:
            return {"status" : "success", "output": False}



    def wait_for_nodes(self, duration=600):
        """User defined method in Child Class
           Waits for all the linecards and RPs (detected in inventory)
           to be up before returning True.
           If 'duration' is exceeded, returns False.
 
           Use this method to wait for the system to be ready
           before installing packages or applying configuration.

           :param duration: Duration for which the script must
                            wait for nodes to be up.
                            Default Value is 600 seconds. 
           :type duration: int

           :return: Returns a True or False  
           :rtype: bool 
        """
        nodes_up = False
        t_end = time.time() + duration 
        while time.time() < t_end:
            nodes_check = self.all_nodes_ready()

            if nodes_check["status"] == "success":
                if nodes_check["output"]:
                    nodes_up = True
                else:
                    nodes_up = False

            else:
                self.syslogger.info("Failed to check if nodes are up, bailing out")
                self.syslogger.info(nodes_check["output"])

            if nodes_up:
                self.syslogger.info("All nodes up")
                return nodes_up
            else:
                self.syslogger.info("All nodes are not up")
                time.sleep(10)

        if not nodes_up:
            self.syslogger.info("All nodes did not come up, exiting")
            return nodes_up




    def install_xr_update(self, package_url):
        """ Method to install XR packages through initial download followed
            by local install and cleanup
            Uses install update utility
            :param package_url: Complete URL of the package to be downloaded
                                and installed
            :type package_url: str
            :return: Dictionary specifying success/error and an associated message
                     {'status': 'success/error',
                      'output': 'success/error message',
                      'warning': 'warning if cleanup fails'}
            :rtype: dict
        """

        result = {"status": "error", "output" : "Installation of package  failed!"}

        # First download the package to the /misc/app_host/scratch folder

        output = self.download_file(package_url, destination_folder="/misc/app_host/scratch")

        if output["status"] == "error":
            if self.debug:
                self.logger.debug("Package Download failed, aborting installation process")
            self.syslogger.info("Package Download failed, aborting installation process")

            return result

        elif output["status"] == "success":
            if self.debug:
                self.logger.debug("Package Download complete, starting installation process")

            self.syslogger.info("Package Download complete, starting installation process")

            rpm_name = output["filename"]
            rpm_location = output["folder"]
            rpm_path = os.path.join(rpm_location, rpm_name)

            ## Query the downloaded RPM to figure out the package name
            cmd = 'rpm -qp ' + str(rpm_path)
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            out, err = process.communicate()

            if process.returncode:
                if self.debug:
                    self.logger.debug("Failed to get the Package name from downloaded RPM, aborting installation process")
                self.syslogger.info("Failed to get the Package name from downloaded RPM, aborting installation process")

                result["status"] = "error"
                result["output"] = "Failed to get the package name from RPM %s" % rpm_name

                # Cleanup
                try:
                    os.remove(rpm_path)
                except OSError:
                    result["warning"] = "failed to remove RPM from path: "+str(rpm_path)
                return result

            else:
                package_name = out.rstrip()
                if package_name.endswith('.x86_64'):
                    package_name = package_name[:-len('.x86_64')]
                else:
                    result["status"] = "error"
                    result["output"] = "Package name %s does not end with x86_64 for  RPM %s" % (package_name, rpm_name)

                    # Cleanup
                    try:
                        os.remove(rpm_path)
                    except OSError:
                        result["warning"] = "failed to remove RPM from path: "+str(rpm_path)
                    return result

                # Now install the package using install update

                install_update = self.xrcmd({"exec_cmd" : "install update source  %s %s" % (rpm_location, rpm_name)})

                if install_update["status"] == "success":
                    t_end = time.time() + 60 * 5
                    while time.time() < t_end:

                        install_active = self.xrcmd({"exec_cmd" : "show install active"})

                        if install_active["status"] == "error":
                            result["status"] = "error"
                            result["output"] = "Failed to fetch output of show install active -Installation of package %s failed" % package_name
                            # Cleanup
                            try:
                                os.remove(rpm_path)
                            except OSError:
                                result["warning"] = "failed to remove RPM from path: "+str(rpm_path)

                            return result

                        # Fetch the number of active nodes on the chassis
                        show_active_nodes = self.xrcmd({"exec_cmd" : "show platform vm"})
                        if show_active_nodes["status"] == "error":
                            result["status"] = "error"
                            result["output"] = "Failed to fetch output of show platform vm -Installation of package %s failed" % package_name
                            # Cleanup
                            try:
                                os.remove(rpm_path)
                            except OSError:
                                result["warning"] = "failed to remove RPM from path: "+str(rpm_path)

                            return result

                        active_node_list = show_active_nodes["output"]
                        active_nodes = len(active_node_list[2:])

                        # Since package must get installed on every node, get the count of number of installations for the package
                        install_count = ''.join(install_active["output"]).count(package_name)
                        # Install count must match the active node count

                        if install_count == active_nodes:
                            if self.debug:
                                self.logger.debug("Installation of %s package successful" % package_name)
                            self.syslogger.info("Installation of %s package successsful" % package_name)

                            result["status"] = "success"
                            result["output"] = "Installation of %s package successful" % package_name

                            # Cleanup
                            try:
                                os.remove(rpm_path)
                            except OSError:
                                result["warning"] = "failed to remove RPM from path: "+str(rpm_path)

                            break
                        else:
                            # Sleep for 10 seconds before checking again
                            time.sleep(10)
                            if self.debug:
                                self.logger.debug("Waiting for installation of %s package to complete" % package_name)
                            self.syslogger.info("Waiting for installation of %s package to complete" % package_name)

                    if result["status"] == "error":
                        result["output"] =  "Installation of %s package timed out" % package_name
                        # Cleanup
                        try:
                            os.remove(rpm_path)
                        except OSError:
                            result["warning"] = "failed to remove RPM from path: "+str(rpm_path)


                    return result
                else:
                    result["status"] = "error"
                    result["output"] = "Failed to execute install update command for package: %s" % package_name
                    # Cleanup
                    try:
                        os.remove(rpm_path)
                    except OSError:
                        result["warning"] = "failed to remove RPM from path: "+str(rpm_path)
                    return result



    def install_xr_add_activate(self, package_url):
        """ Method to install XR packages through initial download followed
            by local install and cleanup
 
            Uses install add+activate utilities
            :param package_url: Complete URL of the package to be downloaded
                                and installed
            :type package_url: str
            :return: Dictionary specifying success/error and an associated message
                     {'status': 'success/error',
                      'output': 'success/error message',
                      'warning': 'warning if cleanup fails'}
            :rtype: dict
        """

        result = {"status": "error", "output" : "Installation of package  failed!"}

        # First download the package to the /misc/app_host/scratch folder

        output = self.download_file(package_url, destination_folder="/misc/app_host/scratch")

        if output["status"] == "error":
            if self.debug:
                self.logger.debug("Package Download failed, aborting installation process")
            self.syslogger.info("Package Download failed, aborting installation process")

            return result

        elif output["status"] == "success":
            if self.debug:
                self.logger.debug("Package Download complete, starting installation process")

            self.syslogger.info("Package Download complete, starting installation process")

            rpm_name = output["filename"]
            rpm_location = output["folder"]
            rpm_path = os.path.join(rpm_location, rpm_name)

            ## Query the downloaded RPM to figure out the package name
            cmd = 'rpm -qp ' + str(rpm_path)
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            out, err = process.communicate()

            if process.returncode:
                if self.debug:
                    self.logger.debug("Failed to get the Package name from downloaded RPM, aborting installation process")
                self.syslogger.info("Failed to get the Package name from downloaded RPM, aborting installation process")

                result["status"] = "error"
                result["output"] = "Failed to get the package name from RPM %s" % rpm_name

                # Cleanup
                try:
                    os.remove(rpm_path)
                except OSError:
                    result["warning"] = "failed to remove RPM from path: "+str(rpm_path)
                return result

            else:
                package_name = out.rstrip()
                if package_name.endswith('.x86_64'):
                    package_name = package_name[:-len('.x86_64')]
                else:
                    result["status"] = "error"
                    result["output"] = "Package name %s does not end with x86_64 for  RPM %s" % (package_name, rpm_name)

                    # Cleanup
                    try:
                        os.remove(rpm_path)
                    except OSError:
                        result["warning"] = "failed to remove RPM from path: "+str(rpm_path)
                    return result 
                   
                # Run the install add command in XR exec 

                install_add = self.xrcmd({"exec_cmd" : "install add source %s %s" % (rpm_location, rpm_name)})

                if install_add["status"] == "success":
                    t_end = time.time() + 60 * 5
                    while time.time() < t_end: 
                            
                        install_inactive = self.xrcmd({"exec_cmd" : "show install inactive"})
                            
                        if install_inactive["status"] == "error":
                            result["status"] = "error"
                            result["output"] = "Failed to fetch output of show install inactive -Installation of package %s failed" % package_name
                            # Cleanup
                            try:
                                os.remove(rpm_path)
                            except OSError:
                                result["warning"] = "failed to remove RPM from path: "+str(rpm_path)
                        
                            return result
                        else:
                            inactive_packages =  install_inactive["output"][1:]
                            if package_name in inactive_packages:
                                self.logger.debug("Install add successful, ready to activate package %s" % (package_name)) 
                                break 
                            else:
                                # Sleep for 10 seconds before checking again
                                time.sleep(10)
                                if self.debug:
                                    self.logger.debug("Waiting for install add of %s package to complete" % package_name)
                                self.syslogger.info("Waiting for install add of  %s package to complete" % package_name)

                else:
                    result["status"] = "error"
                    result["output"] = "Failed to execute install add command for rpm: %s" % rpm_name
                    # Cleanup
                    try:
                        os.remove(rpm_path)
                    except OSError:
                        result["warning"] = "failed to remove RPM from path: "+str(rpm_path)
                    return result




                # Now activate the package

                install_activate = self.xrcmd({"exec_cmd" : "install activate %s" % (package_name)})
                
                if install_activate["status"] == "success":
                    t_end = time.time() + 60 * 5
                    while time.time() < t_end:

                        install_active = self.xrcmd({"exec_cmd" : "show install active"})

                        if install_active["status"] == "error":
                            result["status"] = "error"
                            result["output"] = "Failed to fetch output of show install active -Installation of package %s failed" % package_name
                            # Cleanup
                            try:
                                os.remove(rpm_path)
                            except OSError:
                                result["warning"] = "failed to remove RPM from path: "+str(rpm_path)

                            return result

                        # Fetch the number of active nodes on the chassis
                        show_active_nodes = self.xrcmd({"exec_cmd" : "show platform vm"})
                        if show_active_nodes["status"] == "error":
                            result["status"] = "error"
                            result["output"] = "Failed to fetch output of show platform vm -Installation of package %s failed" % package_name
                            # Cleanup
                            try:
                                os.remove(rpm_path)
                            except OSError:
                                result["warning"] = "failed to remove RPM from path: "+str(rpm_path)

                            return result

                        active_node_list = show_active_nodes["output"]
                        active_nodes = len(active_node_list[2:])

                        # Since package must get installed on every node, get the count of number of installations for the package
                        install_count = ''.join(install_active["output"]).count(package_name)
                        # Install count must match the active node count

                        if install_count == active_nodes:
                            if self.debug:
                                self.logger.debug("Installation of %s package successful" % package_name)
                            self.syslogger.info("Installation of %s package successsful" % package_name)

                            result["status"] = "success"
                            result["output"] = "Installation of %s package successful" % package_name

                            # Cleanup
                            try:
                                os.remove(rpm_path)
                            except OSError:
                                result["warning"] = "failed to remove RPM from path: "+str(rpm_path)

                            break
                        else:
                            # Sleep for 10 seconds before checking again
                            time.sleep(10)
                            if self.debug:
                                self.logger.debug("Waiting for installation of %s package to complete" % package_name)
                            self.syslogger.info("Waiting for installation of %s package to complete" % package_name)

                    if result["status"] == "error":
                        result["output"] =  "Installation of %s package timed out" % package_name
                        # Cleanup
                        try:
                            os.remove(rpm_path)
                        except OSError:
                            result["warning"] = "failed to remove RPM from path: "+str(rpm_path)


                    return result
                else:
                    result["status"] = "error"
                    result["output"] = "Failed to execute install activate command for package: %s" % package_name
                    # Cleanup
                    try:
                        os.remove(rpm_path)
                    except OSError:
                        result["warning"] = "failed to remove RPM from path: "+str(rpm_path)
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



    def get_replace_config(self, url=None, caption=None):
        """User defined method in Child Class
           Downloads IOS-XR config from specified 'url'
           and replaces config to the box. 

           Leverages xrreplace() method in ZtpHelpers Class.

           :param url: Complete url for config to be downloaded 
           :type url: str 
           :type caption: str 

           :return: Return a dictionary with status and output
                    { 'status': 'error/success', 'output': 'output from xrreplace/custom error' }
           :rtype: dict
        """

        result = {"status" : "error", "output" : "", "warning" : ""}

        # Download configuration file
        if url is not None:
            download = self.download_file(url, destination_folder="/root/")
        else:
            self.syslogger.info("URL not specified")
            result["output"] = "URL not specified"
            return result

        if download["status"] == "error":
            self.syslogger.info("Config Download failed")
            result["output"] = "Config Download failed"
            return result
 
            
        file_path = os.path.join(result["folder"], result["filename"])
    
        if caption is None:
            caption = "Configuration Applied through ZTP python"

        # Apply Configuration file
        config_replace = self.xrreplace(result)

        if config_replace["status"] == "error":
            self.syslogger.info("Failed to apply config: Config Apply result = %s" % config_replace["output"])
            result["output"] = config_replace["output"]
            return result


        # Download and config application successful, mark for success

        result["status"] = "success"
        try:
            os.remove(file_path)
        except OSError:
            self.syslogger.info("Failed to remove downloaded config file")
            result["output"] = config_replace["output"]
            result["warning"] = "Failed to remove downloaded config file @ %s" % file_path
        return result


    def run_bash(self, cmd=None):
        """User defined method in Child Class
           Wrapper method for basic subprocess.Popen to execute 
           bash commands on IOS-XR.

           :param cmd: bash command to be executed in XR linux shell. 
           :type cmd: str 
           
           :return: Return a dictionary with status and output
                    { 'status': '0 or non-zero', 
                      'output': 'output from bash cmd' }
           :rtype: dict
        """
        ## In XR the default shell is bash, hence the name
        if cmd is not None:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            out, err = process.communicate()
        else:
            self.syslogger.info("No bash command provided")


        status = process.returncode

        return {"status" : status, "output" : out}



    def get_peer_rp_ip(self):
        """User defined method in Child Class
           IOS-XR internally use a private IP address space
           to reference linecards and RPs.
 
           This method uses XR internal binaries to fetch the
           internal IP address of the Peer RP in an HA setup.

           :param url: Complete url for config to be downloaded 
           :param caption: Any reason to be specified when applying 
                           config. Will show up in the output of:
                          "show configuration commit list detail" 
           :type url: str 
           :type caption: str 


           :return: Return a dictionary with status and the peer RP IP 
                    { 'status': 'error/success', 
                      'peer_rp_ip': 'IP address of Peer RP' }
           :rtype: dict
        """
        cmd = "ip netns exec xrnns /pkg/bin/node_list_generation -f MY"
        bash_out = self.run_bash(cmd)
        if not bash_out["status"]:
            my_name = bash_out["output"]
        else:
            self.syslogger.info("Failed to get My Node Name")
            return {"status" : "error", "peer_rp_ip" : ""}

        cmd = "ip netns exec xrnns /pkg/bin/node_conversion -N " + str(my_name)
        bash_out = self.run_bash(cmd)
        if not bash_out["status"]:
            my_node_name = bash_out["output"].replace('\n', '')
        else:
            self.syslogger.info("Failed to convert My Node Name")
            return {"status" : "error", "peer_rp_ip" : ""}


        cmd = "ip netns exec xrnns /pkg/bin/node_list_generation -f ALL"
        bash_out = self.run_bash(cmd)

        if not bash_out["status"]:
            node_name_list = bash_out["output"].split()
        else:
            self.syslogger.info("Failed to get Node Name List")
            return {"status" : "error", "peer_rp_ip" : ""}

        
        for node in node_name_list:
            if "RP" in node:
                if my_node_name != node:
                    cmd="ip netns exec xrnns /pkg/bin/admin_nodeip_from_nodename -n " + str(node)
                    bash_out = self.run_bash(cmd)
       
                    if not bash_out["status"]:
                        return {"status" : "success", "peer_rp_ip" : bash_out["output"]}
                    else:
                        self.syslogger.info("Failed to get Peer RP IP")
                        return {"status" : "error", "peer_rp_ip" : ""}

        self.syslogger.info("There is no standby RP!")            
        return {"status" : "error", "peer_rp_ip" : ""}
 


    def scp_to_standby(self, src_file_path=None, dest_file_path=None):
        """User defined method in Child Class
           Used to scp files from active to standby RP.
           
           leverages the get_peer_rp_ip() method above.
           Useful to keep active and standby in sync with files 
           in the linux environment.

           :param src_file_path: Source file location on Active RP 
           :param dest_file_path: Destination file location on Standby RP 
           :type src_file_path: str 
           :type dest_file_path: str 

           :return: Return a dictionary with status based on scp result. 
                    { 'status': 'error/success' }
           :rtype: dict
        """

        if any([src_file_path, dest_file_path]) is None:
            self.syslogger.info("Incorrect File path\(s\)") 
            return {"status" : "error"}

        standby_ip = self.get_peer_rp_ip()

        if standby_ip["status"] == "error":
            return {"status" : "error"}
        else:
            self.syslogger.info("Transferring file "+str(src_file_path)+" from Active RP to standby location: " +str(dest_file_path))
            cmd = "ip netns exec xrnns scp "+str(src_file_path)+ " root@" + str(standby_ip["peer_rp_ip"]) + ":" + str(dest_file_path)
            bash_out = self.run_bash(cmd)

            if bash_out["status"]:
                self.syslogger.info("Failed to transfer file to standby")
                return {"status" : "error"}
            else:
                return {"status" : "success"}


            
    def execute_cmd_on_standby(self, cmd=None): 
        """User defined method in Child Class
           Used to execute bash commands on the standby RP
           and fetch the output over SSH.

           Leverages get_peer_rp_ip() and run_bash() methods above.

           :param cmd: bash command to execute on Standby RP 
           :type cmd: str 

           :return: Return a dictionary with status and output
                    { 'status': 'error/success', 
                      'output': 'empty/output from bash cmd on standby' }
           :rtype: dict
        """

        if cmd is None:
            self.syslogger.info("No command specified")
            return {"status" : "error", "output" : ""}
        else:
            with tempfile.NamedTemporaryFile(delete=True) as f:
                f.write("#!/bin/bash\n%s" % cmd)
                f.flush()
                f.seek(0,0)
                standby_ip = self.get_peer_rp_ip()
                if standby_ip["status"] == "error":
                    return {"status" : "error", "output" : ""}
                standby_cmd = "ip netns exec xrnns ssh root@"+str(standby_ip["peer_rp_ip"])+ " " + "\"$(< "+str(f.name)+")\"" 
               
                bash_out = self.run_bash(standby_cmd)

                if bash_out["status"]:
                    self.syslogger.info("Failed to execute command on standby")
                    return {"status" : "error", "output" : ""}
                else:
                    return {"status" : "success", "output": bash_out["output"]}



    def cron_job(self, croncmd=None, croncmd_fname=None, cronfile=None, standby=False, action="add"):
        """User defined method in Child Class
           Pretty useful method to cleanly add or delete cronjobs 
           on the active and/or standby RP.


           Leverages execute_cmd_on_standby(), scp_to_standby() methods defined above

           :param croncmd: croncmd to be added to crontab on Active RP 
           :param croncmd_fname: user can specify a custom name for the file to create under
                                 /etc/cron.d . If not specified, then the name is randomly generated
                                 in the following form:
                                 /etc/cron.d/ztp_cron_timestamp
                                 where timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
 
 
           :param cronfile: Absolute Path to user specified cronfile to blindly place and activate. 
                            Name of the target file under /etc/cron.d will be the same as original filename.
                            If both croncmd and cronfile are provided at the same time, then
                            cronfile will be preferred.
           :param standby: Flag to indicate if the cronjob should be synced to standby RP
                           Default: False 
           :param action: String Flag to indicate whether the croncmd should be added or deleted
                          Default: "add"
                          Available options: "add" | "delete"
           :type croncmd: str 
           :type standby: bool 
           :type active: str

           :return: Return a dictionary with status
                    { 'status': 'error/success' }
           :rtype: dict
        """
        if croncmd is None and cronfile is None:
            self.syslogger.info("No cron job specified, specify either a croncmd or a cronfile")
            return {"status" : "error"}

        # By default cronfile is selected if provided. NO CHECKS will be made on the cronfile, make
        # sure the supplied cronfile is correct.
      

        if action == "add":
            if cronfile is not None:
                ztp_cronfile = "/etc/cron.d/"+ os.path.basename(cronfile)
                try:
                    shutil.copy(cronfile, ztp_cronfile)
                    self.syslogger.info("Successfully added cronfile "+str(cronfile)+" to /etc/cron.d")
                    # Set valid permissions on the cron file
                    if not self.run_bash("chmod 0644 "+ ztp_cronfile)["status"]:
                        self.syslogger.info("Successfully set permissions on cronfile " + ztp_cronfile)
                    else:
                        self.syslogger.info("Failed to set permissions on the cronfile")
                        return {"status" : "error"}
                    if standby:
                        if self.scp_to_standby(ztp_cronfile, ztp_cronfile)["status"]:
                            self.syslogger.info("Cronfile "+ ztp_cronfile+" synced to standby RP!")
                        else:
                            self.syslogger.info("Failed to sync cronfile "+ztp_cronfile+" on standby: "+ str(result["output"]))
                            return {"status" : "error"} 
                except Exception as e:
                    self.syslogger.info("Failed to copy supplied cronfile "+ztp_cronfile+" to /etc/cron.d")
                    self.syslogger.info("Error is "+ str(e))
                    return {"status" : "error"} 
            else:
                # Let's create a file with the required croncmd 

                if croncmd_fname is None:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    ztp_cronfile = "/etc/cron.d/ztp_cron_"+timestamp
                else:
                    ztp_cronfile = "/etc/cron.d/"+str(croncmd_fname)

                try:
                    with open(ztp_cronfile, "w") as fd:
                        fd.write(str(croncmd) + '\n')        
                    self.syslogger.info("Successfully wrote croncmd "+str(croncmd)+" to file"+ztp_cronfile) 

                    # Set valid permissions on the cron file
                    if not self.run_bash("chmod 0644 "+ ztp_cronfile)["status"] == "success":
                        self.syslogger.info("Successfully set permissions on cronfile " + ztp_cronfile)
                    else:
                        self.syslogger.info("Failed to set permissions on the cronfile")
                        return {"status" : "error"}

                    if standby:
                        if self.scp_to_standby(ztp_cronfile, ztp_cronfile)["status"] == "success":
                            self.syslogger.info("Cronfile "+ ztp_cronfile+" synced to standby RP!")
                        else:
                            self.syslogger.info("Failed to sync cronfile "+ztp_cronfile+" on standby: "+ str(result["output"]))
                            return {"status" : "error"}

                except Exception as e:
                    self.syslogger.info("Failed to write supplied croncmd "+str(croncmd)+" to file "+ztp_cronfile)
                    self.syslogger.info("Error is "+ str(e))
                    return {"status" : "error"}


        elif action == "delete":
            # Delete any ztp_cron_timestamp files under /etc/cron.d if no specific file is specified.
            # if cronfile is specified, remove cronfile
            # if croncmd_fname is specified, remove /etc/cron.d/croncmd_fname
            # Else Delete any ztp_cron_timestamp files under /etc/cron.d if no specific file/filename is specified. 

            ztp_cronfiles = []
            if cronfile is not None:
                ztp_cronfiles.append("/etc/cron.d/"+str(os.path.basename(cronfile)))
            elif croncmd_fname is not None:
                ztp_cronfiles.append("/etc/cron.d/"+str(croncmd_fname))
            else:
                # Remove all ztp_cron_* files under /etc/cron.d
                for f in os.listdir("/etc/cron.d"):
                    if re.search("ztp_cron_", f):
                        ztp_cronfiles.append(os.path.join("/etc/cron.d", f))
        
            for ztp_cronfile in ztp_cronfiles:
                try:
                    os.remove(ztp_cronfile)
                    self.syslogger.info("Successfully removed cronfile "+ ztp_cronfile)

                    if self.execute_cmd_on_standby("rm "+ ztp_cronfile)["status"] == "success":
                        self.syslogger.info("Successfully removed cronfile"+ztp_cronfile+" on standby")
                    else:
                        self.syslogger.info("Failed to remove cronfile"+ztp_cronfile+" on standby")
                        return {"status" : "error"}
                except Exception as e:
                    self.syslogger.info("Failed to remove cronfile "+ ztp_cronfile)
                    self.syslogger.info("Error is "+ str(e))
                    return {"status" : "error"}

        return {"status" : "success"}                        



    def is_ha_setup(self):

        rp_count = 0
        show_platform = self.xrcmd({"exec_cmd" : "show platform"})

        if show_platform["status"] == "success":
            try:
                for line in show_platform["output"]:
                    if '/CPU' in line.split()[0]:
                        node_info =  line.split()
                        node_name = node_info[0]
                        if 'RP' in node_name:
                            rp_count = rp_count + 1


                if rp_count in (1,2):
                    return {"status": "success", "rp_count": rp_count}
                else:
                    return {"status": "error", "rp_count": rp_count, "error": "Invalid RP count"}

            except Exception as e:
                if self.debug:
                    self.logger.debug("Error while fetching the RP count")
                    self.logger.debug(e)
                    return {"status": "error", "error": e }

        else:
            if self.debug:
                self.logger.debug("Failed to get the output of show platform")
            return {"status": "error", "output": "Failed to get the output of show platform"}


                    

if __name__ == "__main__":

    # Create an Object of the child class, syslog parameters are optional. 
    # If nothing is specified, then logging will happen to local log rotated file.

    ztp_script = ZtpFunctions(syslog_file=SYSLOG_LOCAL_FILE, syslog_server=SYSLOG_SERVER, syslog_port=SYSLOG_PORT)

    ztp_script.syslogger.info("###### Starting ZTP RUN on NCS5508 ######")

    # Enable verbose debugging to stdout/console. By default it is off
    ztp_script.toggle_debug(1)

    # Change context to XR VRF in the linux shell when needed. Depends on when user changes config to create network namespace.

    # No Config applied yet, so start with global-vrf(default)"
    ztp_script.set_vrf("global-vrf")




    # Set the root user first. Always preferable so that the user can manually gain access to the router in case ZTP script aborts.
    ztp_script.set_root_user()


    # Let's wait for inventory manager to be updated before checking if nodes are ready
    time.sleep(600)

    # Wait for all nodes (linecards, standby etc.)  to be up before installing packages
    # Check for a user defined maximum (time in seconds)
    if ztp_script.wait_for_nodes(120):
        ztp_script.syslogger.info("All Nodes are up!") 
    else:
        ztp_script.syslogger.info("Nodes did not come up! Continuing")
        #sys.exit(1)

    # We've waited and checked long enough, now determine if the system is in HA (standby RP present)

    check_ha = ztp_script.is_ha_setup()

    if check_ha["status"] == "success":
        if check_ha["rp_count"] == 1:
            standby_rp_present = False
            ztp_script.syslogger.info("Standby RP not present, operations will only be performed on Active")
        elif check_ha["rp_count"] == 2:
            standby_rp_present = True
            ztp_script.syslogger.info("Standby RP present, operations will be performed on Active and Standby")
    else:
        ztp_script.syslogger.info("Unable to determine Standby Status on system. Error:"+ check_ha["error"])
        sys.exit(1)


    # Use the parent class helper methods

    ztp_script.syslogger.info("###### Installing k9sec package ######")
    install_result =  ztp_script.install_xr_update(SERVER_URL_PACKAGES + K9SEC_PACKAGE)

    if install_result["status"] == "error":
        ztp_script.syslogger.info("Failed to install k9sec package")
        sys.exit(1)

    ztp_script.syslogger.info("###### install mgbl package ######")
    install_result = ztp_script.install_xr_add_activate(SERVER_URL_PACKAGES + MGBL_PACKAGE)

    if install_result["status"] == "error":
        ztp_script.syslogger.info("Failed to install mgbl package")
        sys.exit(1)


    # To make sure xr packages remain active post reloads, commit them
    ztp_script.syslogger.info("Committing the installed packages")
    install_commit = ztp_script.xr_install_commit(60)

    if install_commit["status"] == "error":
        ztp_script.syslogger.info("Failed to commit installed packages")
        sys.exit(1)


             
    # Download Config with Mgmt vrfs
    output = ztp_script.download_file(SERVER_URL_CONFIGS + CONFIG_FILE, destination_folder="/root/") 

    if output["status"] == "error":
        ztp_script.syslogger.info("Config Download failed, Abort!")
        sys.exit(1)

    ztp_script.syslogger.info("Replacing system config with the downloaded config")
    # Replace existing config with downloaded config file 
    config_apply = ztp_script.xrreplace("/root/" + CONFIG_FILE)

    if config_apply["status"] == "error":
        ztp_script.syslogger.info("Failed to replace existing config")
        ztp_script.syslogger.info("Config Apply result = %s" % config_apply["output"]) 
        try:
            os.remove("/root/" + CONFIG_FILE)
        except OSError:
            ztp_script.syslogger.info("Failed to remove downloaded config file")
        sys.exit(1) 
    
    # VRFs on Mgmt interface are configured by user. Use the set_vrf helper method to set proper
    # context before continuing. 
    # Syslog and download operations are covered by the set vrf utility by default.
    # For any other shell commands that utilize the network, 
    # change context to vrf using `ip netns exec <vrf>` before the command

    ztp_script.set_vrf("mgmt")
    ztp_script.syslogger.info("###### Changed context to user specified VRF based on config ######")
    ztp_script.syslogger.info("Base config applied successfully")
    ztp_script.syslogger.info("Config Apply result = %s" % config_apply["output"])


    # Install crypto keys
    show_pubkey = ztp_script.xrcmd({"exec_cmd" : "show crypto key mypubkey rsa"}) 

    if show_pubkey["status"] == "success":
        if show_pubkey["output"] == '':
            ztp_script.syslogger.info("No RSA keys present, Creating...")
            ztp_script.xrcmd({"exec_cmd" : "crypto key generate rsa", "prompt_response" : "2048\\n"})
        else:
            ztp_script.syslogger.info("RSA keys already present, Recreating....")
            ztp_script.xrcmd({"exec_cmd" : "crypto key generate rsa", "prompt_response" : "yes\\n 2048\\n"}) 
    else:
        ztp_script.syslogger.info("Unable to get the status of RSA keys: "+str(show_pubkey["output"]))
        # Not quitting the script because of this failure
   


    ztp_script.syslogger.info("Setting up domain name server in /etc/resolv.conf on Active and Standby RP")

    date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    # Set up the nameserver in /etc/resolv.conf

    resolver = "/etc/resolv.conf"
    domain = "cisco.com"
    nameserver = "2.2.2.2"

    setup_resolver = ["### created by ztp " +str(date) + " ###" ,
                      "domain "+str(domain),
                      "search "+str(domain),
                      "nameserver "+str(nameserver)] 
                      
    with open(resolver, 'w') as resolver_fh:
        resolver_fh.write('\n'.join(setup_resolver))


    if standby_rp_present:
        # Now sync the resolver file to standby
        standby_scp = ztp_script.scp_to_standby(src_file_path=resolver, dest_file_path=resolver)
    
        if standby_scp["status"] == "error":
            ztp_script.syslogger.info("Failed to transfer resolver file to standby")
            sys.exit(1)


    # Set up access to yum repository for Puppet. User could do a direct download and install via rpm as well

    ztp_script.syslogger.info("Setting up yum repo for puppet RPM install on Active and Standby RP")

    yum_repo = SERVER_URL_PACKAGES 
    puppet_yum_conf = "/etc/yum/repos.d/puppet.repo"

    setup_yum_repo = ["### created by ztp "+str(date)+ " ###",
                      "[puppetlabs]",
                      "name=puppetlabs",
                      "enabled=1",
                      "gpgcheck=1",
                      "baseurl="+str(yum_repo)]

    with open(puppet_yum_conf, 'w') as puppet_yum_conf_fh:
        puppet_yum_conf_fh.write('\n'.join(setup_yum_repo))


    if standby_rp_present:
        # Now sync the puppet yum config file to standby
        standby_scp = ztp_script.scp_to_standby(src_file_path=puppet_yum_conf, dest_file_path=puppet_yum_conf)

        if standby_scp["status"] == "error":
            ztp_script.syslogger.info("Failed to transfer puppet yum config file to standby")
            sys.exit(1)


    # Download GPG KEYS for puppet install

    ztp_script.syslogger.info("Dowloading GPG keys for puppet install to active and standby RP(if present)") 


    gpg_keys_list = ["RPM-GPG-KEY-puppet",
                     "RPM-GPG-KEY-puppetlabs",
                     "RPM-GPG-KEY-reductive"]


    for gpg_key in gpg_keys_list:
        download_gpg = ztp_script.download_file(SERVER_URL_PACKAGES+str(gpg_key), destination_folder="/root/")

        if download_gpg["status"] == "error":
            ztp_script.syslogger.info("Failed to download "+str(gpg_key))
            sys.exit(1)

        filename = download_gpg["filename"]
        folder = download_gpg["folder"]
        filepath = os.path.join(folder, filename)

        if standby_rp_present:
            # Transfer gpg key to standby as well
            standby_scp = ztp_script.scp_to_standby(src_file_path=filepath, dest_file_path=filepath)

            if standby_scp["status"] == "error":
                ztp_script.syslogger.info("Failed to transfer gpg key to standby")
                sys.exit(1)

        # Import the GPG Key on Active and Standby (if present)
        ztp_script.syslogger.info("Importing GPG key:"+str(gpg_key)+"on active")
        rpm_import = ztp_script.run_bash("rpm --import /root/"+str(gpg_key))
 
        if rpm_import["status"] == "error":
            ztp_script.syslogger.info("Failed to import GPG Key:"+str(gpg_key)+"on active")
            sys.exit(1)


        if standby_rp_present:
            ztp_script.syslogger.info("Importing GPG key:"+str(gpg_key)+"on standby")
            standby_rpm_import = ztp_script.execute_cmd_on_standby("rpm --import /root/"+str(gpg_key))
            if standby_rpm_import["status"] == "error":
                ztp_script.syslogger.info("Failed to import GPG Key:"+str(gpg_key)+"on standby")
                sys.exit(1)



    # Now let's start installing puppet on the Active and Standby(if present)

    vrf_exec = "ip netns exec "+str(ztp_script.vrf)

    puppet_install_cmdlist = ["/usr/bin/yum clean all > /dev/null",
                             str(vrf_exec) + " /usr/bin/yum update > /dev/null",
                             str(vrf_exec) + " /usr/bin/yum install -y --downloadonly --downloaddir=/root/ puppet > /dev/null",
                             str(vrf_exec) + " /usr/bin/yum install -y /root/puppet*.rpm"]


    for cmd in puppet_install_cmdlist:
        result = ztp_script.run_bash(cmd)

        if result["status"] == "error":
            ztp_script.syslogger.info("Failed to execute command on Active: " + str(cmd))
            #sys.exit(1)


    if standby_rp_present:
        # Transfer puppet RPM to standby to install
        standby_scp = ztp_script.scp_to_standby(src_file_path='/root/puppet*.rpm', dest_file_path='/root/')

        if standby_scp["status"] == "error":
            ztp_script.syslogger.info("Failed to transfer puppet RPM to standby")
            sys.exit(1)

        standby_rpm_install = ztp_script.execute_cmd_on_standby("/usr/bin/rpm -ivh /root/puppet*.rpm > /dev/null")
        if standby_rpm_install["status"] == "error":
            ztp_script.syslogger.info("Failed to install Puppet RPM on standby")
            #sys.exit(1)



    # Configure Puppet on Active and Standby ( if present) 

    ztp_script.syslogger.info("Configuring puppet on Active and Standby RP(if present)") 

    puppet_conf = "/etc/puppetlabs/puppet/puppet.conf"
    
    setup_puppet_conf = ["### created by ztp "+str(date)+ " ###",
                         "[main]",
                         "server = puppet-master.cisco.local"]

    with open(puppet_conf, 'w') as puppet_conf_fh:
        puppet_conf_fh.write('\n'.join(setup_puppet_conf))


    if standby_rp_present:
        # Now sync the puppet config file to standby
        standby_scp = ztp_script.scp_to_standby(src_file_path=puppet_conf, dest_file_path=puppet_conf)

        if standby_scp["status"] == "error":
            ztp_script.syslogger.info("Failed to transfer puppet yum config file to standby")
            sys.exit(1)


    ztp_script.syslogger.info("Downloading and setting up python Cronjob to start daemons in event of switchover")
    download_cron = ztp_script.download_file(SERVER_URL_SCRIPTS + CRON_SCRIPT, destination_folder="/root/")

    if download_cron["status"] == "error":
        ztp_script.syslogger.info("Unable to download cron job!")
        sys.exit(1)


    filename = download_cron["filename"]
    folder = download_cron["folder"]
    filepath = os.path.join(folder, filename)


    if standby_rp_present:
        # Transfer cronjob script to standby as well
        standby_scp = ztp_script.scp_to_standby(src_file_path=filepath, dest_file_path=filepath)

        if standby_scp["status"] == "error":
            ztp_script.syslogger.info("Failed to transfer cronjob script to standby")
            sys.exit(1)


    #Create the cron cmd 
    croncmd = "* * * * * root PATH=/sbin:/usr/sbin:/bin:/usr/bin:${PATH};/usr/bin/python " + str(filepath)

    # Set up cronjob on active and standby(if present)

    cron_setup = ztp_script.cron_job(croncmd = croncmd, standby=standby_rp_present, action="add")

    if cron_setup["status"] == "error":
        ztp_script.syslogger.info("Unable to set up cron Job, quitting ZTP script")
        sys.exit(1)



    ztp_script.syslogger.info("ZTP complete!")
    sys.exit(0)
