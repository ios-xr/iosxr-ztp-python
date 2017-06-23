#!/usr/bin/env python

import sys, os, subprocess
sys.path.append("/pkg/bin/")
from ztp_helper import ZtpHelpers
import json, tempfile, time
from time import gmtime, strftime

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
                     username netops
                     group root-lr
                     group cisco-support
                     secret 5 $1$7kTu$zjrgqbgW08vEXsYzUycXw1
                     !
                     end"""



        with tempfile.NamedTemporaryFile(delete=True) as f:
            f.write("%s" % config)
            f.flush()
            f.seek(0)
            result = self.xrapply(f.name)

        if result["status"] == "error":

            self.syslogger.info("Failed to apply root user to system %s"+json.dumps(result))

        return result


    def wait_for_nodes(self, duration=600):
        """User defined method in Child Class
           Waits for all the linecards and RPs (detected in inventory)
           to be up before returning True.
           If 'duration' is exceeded, returns False.
 
           Use this method to wait for the system to be ready
           before installing packages or applying configuration.

           Leverages all_nodes_ready() method in ZtpHelpers Class.

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



    def get_apply_config(self, url=None, caption=None):
        """User defined method in Child Class
           Downloads IOS-XR config from specified 'url'
           and applies config to the box. 

           Leverages xrapply() method in ZtpHelpers Class.

           :param url: Complete url for config to be downloaded 
           :param caption: Any reason to be specified when applying 
                           config. Will show up in the output of:
                          "show configuration commit list detail" 
           :type url: str 
           :type caption: str 

           :return: Return a dictionary with status and output
                    { 'status': 'error/success', 'output': 'output from xrapply/custom error' }
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
        config_apply = self.xrapply(result, reason=caption)

        if config_apply["status"] == "error":
            self.syslogger.info("Failed to apply config: Config Apply result = %s" % config_apply["output"])
            result["output"] = config_apply["output"]
            return result


        # Download and config application successful, mark for success

        result["status"] = "success"
        try:
            os.remove(file_path)
        except OSError:
            self.syslogger.info("Failed to remove downloaded config file")
            result["output"] = config_apply["output"]
            result["warning"] = "Failed to remove downloaded config file @ %s" % file_path
        return result


    def run_bash(self, cmd=None):
        """User defined method in Child Class
           Wrapper method for basic subprocess.Popen to execute 
           bash commands on IOS-XR.

           :param cmd: bash command to be executed in XR linux shell. 
           :type cmd: str 
           
           :return: Return a dictionary with status and output
                    { 'status': 'error/success', 
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

            
    def cron_job(self, croncmd=None, standby=False, action="add"): 
        """User defined method in Child Class
           Pretty useful method to cleanly add or delete cronjobs 
           on the active and/or standby RP.

           Also cleans up after itself and prevents duplication of cronjobs.

           Leverages execute_cmd_on_standby(), scp_to_standby() methods above
           and xrcmd() method from Parent ZtpHelpers class.

           :param croncmd: croncmd to be added to crontab on Active RP 
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
        if croncmd is None:
            self.syslogger.info("No cron job specified")
            return {"status" : "error", "output" : ""}
 
        ## Create a Named temp file to help replace the current cronjob file

        
        with tempfile.NamedTemporaryFile(delete=True) as f:
            cmd = "crontab -l > " + str(f.name)
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            out, err = process.communicate()

            if process.returncode:
                self.syslogger.info("Failed to dump current crontab into Temp file")
                return {"status" : "error"}
            else:
                f.flush()
                f.seek(0, 0)
                cronlines = [line.rstrip() for line in f.readlines()]
                # Check that croncmd appears in the current crontab
                if croncmd in cronlines:
                    # croncmd already exists in existing crontab
                    if action == "add":
                        self.syslogger.info("cronjob already present, skipping add")
                        return {"status" : "success"}
                    elif action == "delete":
                        # Remove the croncmd from crontab list - deletes all occurences
                        cronlines[:] = (line for line in cronlines if line != croncmd)
                        self.syslogger.info("Deleting cronjob as instructed")
                        # Dial back to the beginning of the file
                        f.seek(0,0) 
                        for line in cronlines:
                            f.write(str(line) + '\n')
                        f.truncate()
                        f.flush()
                        f.seek(0,0)
                    else:
                        self.syslogger.info("Invalid action specified. Choose between \"add\" and \"delete\"")
                        return {"status" : "error"}
                else:
                    if action == "add":
                        # Move to the end of the file before adding the croncmd
                        f.seek(0, os.SEEK_END)
                        f.write(str(croncmd) + '\n')
                        # flush and  write to disk
                        f.flush()
                        f.seek(0,0) 
                        self.syslogger.info("Adding Cronjob as instructed")
                    elif action == "delete":
                        self.syslogger.info("cronjob doesn't exist already, skipping delete")
                        return {"status" : "success"}

                    else:
                        self.syslogger.info("Invalid action specified. Choose between \"add\" and \"delete\"")
                        return {"status" : "error"}


               # Now replace the current crontab with the tempfile contents


               # cmd = "crontab  " + str(f.name)
               # process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
               # out, err = process.communicate()

               # if process.returncode:
               #     self.syslogger.info("Failed to modify crontab: "+str(out))
               #     return {"status" : "error"}


                # Workaround technique using xrcmd till ulimit stack size is increased.
                cmd = "bash -c crontab " + str(f.name)
                crontab_change = self.xrcmd({"exec_cmd" : cmd})
               
                process = subprocess.Popen('crontab -l', stdout=subprocess.PIPE, shell=True)
                out, err = process.communicate()

                if process.returncode:
                    self.syslogger.info("Failed to get crontab: "+str(out))
                    return {"status" : "error"} 

               
                f.seek(0,0)
                if f.read() == out:
                    self.syslogger.info("Cronjob updated on active RP!")
                else:
                    self.syslogger.info("Failed to modify crontab on active RP!")
                    return {"status" : "error"}
    
                if standby:
                    #User requested to create the same cron job on the standby 
                    # First sync the tempfile to the standby
                    if self.scp_to_standby(f.name, f.name)["status"] == "success":
                        # Now execute the remote command to sync crontab
                        cmd = "crontab  " + str(f.name)
                        result = self.execute_cmd_on_standby(cmd)
                        if result["status"] == "success":
                            #remove tempfile from standby
                            remove = self.execute_cmd_on_standby("rm "+str(f.name))#
                            if remove["status"] == "success":
                                self.syslogger.info("Cronjob updated on standby RP!")
                                return {"status" : "success"}
                            else:
                                return {"status" : "success", "warning" : "failed to remove tempfile on standby"}
                        else:
                            self.syslogger.info("Failed to modify crontab on standby: "+ str(result["output"]))
                            #remove tempfile from standby
                            remove = self.execute_cmd_on_standby("rm "+str(f.name))
                            if remove["status"] == "success":
                                return {"status" : "error"}
                            else:
                                return {"status" : "error", "warning" : "failed to remove tempfile on standby"}

                return {"status" : "success"}


    def is_ha_setup(self):

        rp_count = 0
        show_platform = self.xrcmd({"exec_cmd" : "show platform"})

        if show_platform["status"] == "success":
            try:
                for line in show_platform["output"]:
                    if '/CPU' in line.split()[0]:
                        print line
                        node_info =  line.split()
                        print node_info
                        node_name = node_info[0]
                        print node_name
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

    ztp_script = ZtpFunctions(syslog_file="/root/ztp_python.log", syslog_server="11.11.11.2", syslog_port=514)

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
    if ztp_script.wait_for_nodes(600):
        ztp_script.syslogger.info("All Nodes are up!") 
    else:
        ztp_script.syslogger.info("Nodes did not come up! Abort!")
        sys.exit(0)

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
        sys.exit(0)


    # Use the parent class helper methods

    ztp_script.syslogger.info("###### Installing k9sec package ######")
    install_result =  ztp_script.install_xr_package("http://11.11.11.2:9090/packages/ncs5500-k9sec-2.2.0.0.x86_64.rpm")

    if install_result["status"] == "error":
        ztp_script.syslogger.info("Failed to install k9sec package")
        sys.exit(0)

    ztp_script.syslogger.info("###### install mgbl package ######")
    install_result = ztp_script.install_xr_package("http://11.11.11.2:9090/packages/ncs5500-mgbl-3.0.0.0.x86_64.rpm")

    if install_result["status"] == "error":
        ztp_script.syslogger.info("Failed to install mgbl package")
        sys.exit(0)


    # To make sure xr packages remain active post reloads, commit them
    ztp_script.syslogger.info("Committing the installed packages")
    install_commit = ztp_script.xr_install_commit(60)

    if install_commit["status"] == "error":
        ztp_script.syslogger.info("Failed to commit installed packages")
        sys.exit(0)


             
    # Download Config with Mgmt vrfs
    output = ztp_script.download_file("http://11.11.11.2:9090/configs/ncs5508_vrf_test.config", destination_folder="/root/") 

    if output["status"] == "error":
        ztp_script.syslogger.info("Config Download failed, Abort!")
        sys.exit(0)

    ztp_script.syslogger.info("Applying downloaded config to System")
    # Apply downloaded config file (merge) 
    config_apply = ztp_script.xrapply("/root/ncs5508_vrf_test.config", reason="Applied Base Config using ZTP python")

    if config_apply["status"] == "error":
        ztp_script.syslogger.info("Failed to apply base config")
        ztp_script.syslogger.info("Config Apply result = %s" % config_apply["output"]) 
        try:
            os.remove("/root/ncs5508_vrf_test.config")
        except OSError:
            ztp_script.syslogger.info("Failed to remove downloaded config file")
        sys.exit(0) 
    
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
    nameserver = "171.70.168.183"

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
            sys.exit(0)


    # Set up access to yum repository for Puppet. User could do a direct download and install via rpm as well

    ztp_script.syslogger.info("Setting up yum repo for puppet RPM install on Active and Standby RP")

    yum_repo = "http://11.11.11.2:9090/packages/"
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
            sys.exit(0)


    # Download GPG KEYS for puppet install

    ztp_script.syslogger.info("Dowloading GPG keys for puppet install to active and standby RP(if present)") 


    gpg_keys_list = ["RPM-GPG-KEY-puppet",
                     "RPM-GPG-KEY-puppetlabs",
                     "RPM-GPG-KEY-reductive"]


    for gpg_key in gpg_keys_list:
        download_gpg = ztp_script.download_file("http://11.11.11.2:9090/packages/"+str(gpg_key), destination_folder="/root/")

        if download_gpg["status"] == "error":
            ztp_script.syslogger.info("Failed to download "+str(gpg_key))
            sys.exit(0)

        filename = download_gpg["filename"]
        folder = download_gpg["folder"]
        filepath = os.path.join(folder, filename)

        if standby_rp_present:
            # Transfer gpg key to standby as well
            standby_scp = ztp_script.scp_to_standby(src_file_path=filepath, dest_file_path=filepath)

            if standby_scp["status"] == "error":
                ztp_script.syslogger.info("Failed to transfer gpg key to standby")
                sys.exit(0)

        # Import the GPG Key on Active and Standby (if present)
        ztp_script.syslogger.info("Importing GPG key:"+str(gpg_key)+"on active")
        rpm_import = ztp_script.run_bash("rpm --import /root/"+str(gpg_key))
 
        if rpm_import["status"] == "error":
            ztp_script.syslogger.info("Failed to import GPG Key:"+str(gpg_key)+"on active")
            sys.exit(0)


        if standby_rp_present:
            ztp_script.syslogger.info("Importing GPG key:"+str(gpg_key)+"on standby")
            standby_rpm_import = ztp_script.execute_cmd_on_standby("rpm --import /root/"+str(gpg_key))
            if standby_rpm_import["status"] == "error":
                ztp_script.syslogger.info("Failed to import GPG Key:"+str(gpg_key)+"on standby")
                sys.exit(0)



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
            sys.exit(0)


    if standby_rp_present:
        # Transfer puppet RPM to standby to install
        standby_scp = ztp_script.scp_to_standby(src_file_path='/root/puppet*.rpm', dest_file_path='/root/')

        if standby_scp["status"] == "error":
            ztp_script.syslogger.info("Failed to transfer puppet RPM to standby")
            sys.exit(0)

        standby_rpm_install = ztp_script.execute_cmd_on_standby("/usr/bin/rpm -ivh /root/puppet*.rpm > /dev/null")
        if standby_rpm_install["status"] == "error":
            ztp_script.syslogger.info("Failed to install Puppet RPM on standby")
            sys.exit(0)



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
            sys.exit(0)


    ztp_script.syslogger.info("Downloading and setting up python Cronjob to start daemons in event of switchover")
    download_cron = ztp_script.download_file("http://11.11.11.2:9090/scripts/cron_action.py", destination_folder="/root/")

    if download_cron["status"] == "error":
        ztp_script.syslogger.info("Unable to download cron job!")
        sys.exit(0)


    filename = download_cron["filename"]
    folder = download_cron["folder"]
    filepath = os.path.join(folder, filename)


    if standby_rp_present:
        # Transfer cronjob script to standby as well
        standby_scp = ztp_script.scp_to_standby(src_file_path=filepath, dest_file_path=filepath)

        if standby_scp["status"] == "error":
            ztp_script.syslogger.info("Failed to transfer cronjob script to standby")
            sys.exit(0)

    #Create the cron cmd 
    croncmd = "* * * * * /usr/bin/python " + str(filepath)

    # Set up cronjob on active and standby(if present)

    cron_setup = ztp_script.cron_job(croncmd = croncmd, standby=standby_rp_present, action="add")

    if cron_setup["status"] == "error":
        ztp_script.syslogger.info("Unable to set up cron Job, quitting ZTP script")
        sys.exit(0)



    # Starting Puppet  
    ztp_script.syslogger.info("ZTP complete!")

