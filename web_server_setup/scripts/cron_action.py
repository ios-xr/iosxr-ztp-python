#!/usr/bin/env python

import sys,os, json, subprocess
sys.path.append('/pkg/bin')
from ztp_helper import ZtpHelpers

class CronAction(ZtpHelpers):

    
    def __init__(self, syslog_file=None, 
                 syslog_server=None, syslog_port=None, 
                 method_list=None):

        self.method_list = method_list
        self.method_mapper = { 'spin_up_docker' : self.spin_up_docker}
        # Initialize the parent ZtpHelpers class as well
        super(CronAction, self).__init__(syslog_file=syslog_file, syslog_server=syslog_server, syslog_port=syslog_port)


    def is_active_rp(self):
        '''method to check if the node executing this script is the active RP
        '''
        # Get the current active RP node-name
        exec_cmd = "show redundancy summary"
        show_red_summary = self.xrcmd({"exec_cmd" : exec_cmd})

        if show_red_summary["status"] == "error":
             self.sylogger.info("Failed to get show redundancy summary output from XR")
             return {"status" : "error", "output" : "", "warning" : "Failed to get show redundancy summary output"}

        else:
            try:
                current_active_rp = show_red_summary["output"][2].split()[0]
            except Exception as e:
                self.syslogger.info("Failed to get Active RP from show redundancy summary output")
                return {"status" : "error", "output" : "", "warning" : "Failed to get Active RP, error: " + str(e)}

        cmd = "/sbin/ip netns exec xrnns /pkg/bin/node_list_generation -f MY"
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        out, err = process.communicate()
        my_node_name = ''

        if not process.returncode:
            my_node_name = out
        else:
            self.syslogger.info("Failed to get My Node Name")
            

        if current_active_rp == my_node_name:
            self.syslogger.info("Cron Job: I am the current RP, take action")
            return {"status" : "success", "output" : True, "warning" : ""}    
        else:
            self.syslogger.info("Cron Job: I am not the current RP")
            return {"status" : "success", "output" : False, "warning" : ""} 

    def take_cron_action(self):
        ''' Wrapper method that executes a set of registered CronAction methods
        '''

        if self.method_list is not None:
            self.syslogger.info("Executing all the Registered Cron functions")
            try:            
                for method in self.method_list:
                    method_obj = self.method_mapper[method["name"]]
                    method_out = method_obj(**method["args"])
                    if method_out["status"] == "error":
                        self.syslogger.info("Error executing cron method: " +str(method_obj.__name__)+ " :" + method_out["output"])
                        return {"status" : "error", "output" : 'method_out["output"]'}
                    else:  
                       self.syslogger.info("Result for cron function: " +str(method_obj.__name__)+" is " + json.dumps(method_obj(**method["args"])))
                return {"status" : "success", "output" : "Successfully executed all cron methods"}
            except Exception as e:
                self.syslogger.info("Failure while executing methodlist: " + str(e))
                return {"status" : "error", "output" : str(e)}


    def _check_docker_running(self, docker_name):
        '''Internal helper method to check if a docker with name docker_name is running
        '''

        cmd = "sudo -i docker ps -f name="+str(docker_name)

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        out, err = process.communicate()

        if not process.returncode:
            docker_state = out 
        else:
            self.syslogger.info("Failed to get docker state")
     
        output_list = []
        output = ''
 
        for line in out.splitlines():
            fixed_line= line.replace("\n", " ").strip()
            output_list.append(fixed_line)
            output = filter(None, output_list)    # Removing empty items

        for line in output:
            if line.split()[-1] == docker_name:
                self.syslogger.info("Docker container " +str(docker_name)+ " is running")
                return {"status" : True}
       
        return {"status" : False}
     


    def spin_up_docker(self, scratch_folder='/misc/app_host/scratch', 
                       docker_name='crondock', docker_image_name='cronimg',
                       docker_image_url=None, docker_cmd='bash'): 
        '''An example of a CronAction method, executed by the take_action method
        '''

        if docker_image_url is None:
            self.syslogger.info("Docker image URL not specified")
            return {"status" : "error", "output" : "Docker image URL not specified"} 
        if self._check_docker_running(docker_name)["status"]:
            self.syslogger.info("Skip cron action")
            return {"status" : "success", "output" : "Docker container already running"}
        else:       
            # Download docker container and spin it up
            docker_download = self.download_file(docker_image_url, destination_folder=scratch_folder)

            if docker_download["status"] == "error":
                self.syslogger.info("Failed to download docker container tar ball")
                return {"status" : "error", "output" : "Failed to download docker container tar ball"} 
            else:
                filename = docker_download["filename"]
                folder = docker_download["folder"]
                filepath = os.path.join(folder, filename)

                cmd = "sudo -i docker import " +str(filepath)+ "  " + str(docker_image_name)
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
                out, err = process.communicate()

                if process.returncode:
                    self.syslogger.info("Failed to import docker image")
                    return {"status" : "error", "output" : "Failed to import docker image"} 
                else:
                    # Remove the downloaded tar ball
                    # We don't know why the container died, so remove properly before continuing
                    try:
                        cmd = "sudo -i docker rm -f "+str(docker_name)
                        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
                        out, err = process.communicate()
                    except:
                        # Ignoring exception ,for the first launch 
                        pass 

                    cmd = "sudo -i docker run -itd --privileged -v /var/run/netns:/var/run/netns --name " +str(docker_name) +  " " + str(docker_image_name) + " " + str(docker_cmd) 
        
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
                    out, err = process.communicate()
 
                    if  process.returncode:
                        self.syslogger.info("Failed to spin up the docker container")
                        return {"status" : "error", "output" : "Failed to spin up the docker container"}
                    else:
                        if self._check_docker_running(docker_name)["status"]:
                            self.syslogger.info("Docker container is now up and running!")
                            return {"status" : "success", "output" : "Docker container is now up and running!"}
                                
                  

if __name__ == "__main__":

    method1 = {}
    method1["name"] = "spin_up_docker"
    method1["args"] = {"scratch_folder" : "/misc/app_host/scratch",
                       "docker_name" : "ubuntu",
                       "docker_image_name" : "ubuntu",
                       "docker_image_url" : "http://11.11.11.2:9090/ubuntu.tar",
                       "docker_cmd" : "bash"} 
    method_list = [method1] 

    cronobj = CronAction(syslog_server="11.11.11.2", 
                         syslog_port=514, 
                         method_list=method_list)
    
    cronobj.set_vrf("mgmt")
    result = cronobj.is_active_rp()

    if result["status"] == "success":
        cronobj.syslogger.info("Executing Cron Actions")
        method_run = cronobj.take_cron_action()
        if method_run["status"] == "error":
            cronobj.syslogger.info("Error executing cron methods on active RP: "+str(method_run["output"]))
        else:
            cronobj.syslogger.info("Successfully ran the Cron Methods on active RP")
   

