#!/usr/bin/env python
"""
  author: akshshar@cisco.com

  ztp_helper.py

  ZTP helper for Python

  Copyright (c) 2017 by cisco Systems, Inc.
  All rights reserved.

"""


import os, sys, subprocess
import logging, logging.handlers
from urllib2 import Request, urlopen, URLError, HTTPError
import urlparse, posixpath, time, json
from ctypes import cdll
libc = cdll.LoadLibrary('libc.so.6')
_setns = libc.setns

CLONE_NEWNET = 0x40000000

class ZtpHelpers(object):

    def __init__(self, syslog_server=None, syslog_port=None, syslog_file=None):
        """__init__ constructor
           :param syslog_server: IP address of reachable Syslog Server 
           :param syslog_port: Port for the reachable syslog server
           :param syslog_file: Alternative or addon file for syslog
           :type syslog_server: str
           :type syslog_port: int
           :type syslog_file:str
        """ 
        
        self.vrf = "global-vrf"
        self.syslog_server=syslog_server
        try:
            self.syslog_port = int(syslog_port)
        except: 
            self.syslog_port = None
        self.syslog_file=syslog_file
        self.setup_syslog()
        self.setup_debug_logger()
        self.debug = False 



    @classmethod
    def setns(cls, fd, nstype):
        """Class Method for setting the network namespace
           :param cls: Reference to the class ZtpHelpers 
           :param fd: incoming file descriptor  
           :param nstype: namespace type for the sentns call
           :type nstype: int  
                  0      Allow any type of namespace to be joined.

                  CLONE_NEWNET = 0x40000000 (since Linux 3.0)
                         fd must refer to a network namespace.
        """
        _setns(fd.fileno(), nstype)


    @classmethod
    def get_netns_path(cls, nspath=None, nsname=None, nspid=None):
        """Class Method to fetch the network namespace filepath 
           associated with a PID or name 
           :param cls: Reference to the class ZtpHelpers
           :param nspath: optional network namespace associated name
           :param nspid: optional network namespace associate PID
           :type nspath: str
           :type nspid: int 
           :return: Return the complete file path 
           :rtype:  str 
        """

        if nsname:
            nspath = '/var/run/netns/%s' % nsname
        elif nspid:
            nspath = '/proc/%d/ns/net' % nspid

        return nspath



    def toggle_debug(self, enable):
        """Enable/disable debug logging
           :param enable: Enable/Disable flag 
           :type enable: int
        """
        if enable:
            self.debug = True
            self.logger.propagate = True 
        else:
            self.debug = False
            self.logger.propagate = False


            
    def set_vrf(self, vrfname=None):
        """Set the VRF (network namespace)
           :param vrfname: Network namespace name 
                           corresponding to XR VRF  
        """
        if vrfname is not None:
            self.vrf = vrfname
        else:
            self.vrf = "global-vrf" 

        # Restart the syslogger service in the new vrf`
        self.syslogger.handlers = []
        self.setup_syslog()
        # Spend some time here to let the network namespaces
        # and interfaces in the XR linux shell converge.
        time.sleep(30)
 
    
    def setup_debug_logger(self):
        """Setup the debug logger to throw debugs to stdout/stderr 
        """

        logger = logging.getLogger('DebugZTPLogger')
        logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        self.logger = logger



    def download_file(self, file_url, destination_folder):
        """Download a file from the specified URL
           :param file_url: Complete URL to download file 
           :param destination_folder: Folder to store the 
                                      downloaded file
           :type file_url: str
           :type destination_folder: str
           :return: Dictionary specifying download success/failure
                    Failure => { 'status' : 'error' }
                    Success => { 'status' : 'success',
                                 'filename' : 'Name of downloaded file',
                                 'folder' : 'Directory location of downloaded file'}
           :rtype: dict 
        """

        with open(self.get_netns_path(nsname=self.vrf)) as fd:
            self.setns(fd, CLONE_NEWNET)

            path = urlparse.urlsplit(file_url).path
            filename = posixpath.basename(path) 

            #create the url and the request
            req = Request(file_url)
        
            # Open the url
            try:
                f = urlopen(req)
                self.syslogger.info("Downloading file %s from URL:%s" % (filename, file_url))

                if self.debug:
                    self.logger.debug("Downloading file %s from URL:%s" % (filename, file_url))
                
                # Open our local file for writing
                destination_path = os.path.join(destination_folder, filename)

                with open(destination_path, "w") as local_file:
                    local_file.write(f.read())
                
            #handle errors
            except HTTPError, e:
                if self.debug: 
                    self.logger.debug("HTTP Error: %s, %s" % (e.code , file_url))

                self.syslogger.info("HTTP Error: %s, %s" % (e.code , file_url))

                return {"status" : "error"}
                                 
            except URLError, e:
                if self.debug:
                    self.logger.debug("URL Error: %s, %s" % (e.reason , file_url))
              
                self.syslogger.info("URL Error: %s, %s" % (e.reason , file_url))
                return {"status" : "error"}
 
        return {"status" : "success", "filename": filename, "folder": destination_folder}



    def setup_syslog(self):
        """Setup up the Syslog logger for remote or local operation
           IMPORTANT:  This logger must be set up in the correct vrf.
        """

        with open(self.get_netns_path(nsname=self.vrf)) as fd:
          self.setns(fd, CLONE_NEWNET)

          address = self.syslog_server 
          port = self.syslog_port
          filename = self.syslog_file


          logger = logging.getLogger('ZTPLogger')
          logger.setLevel(logging.INFO)

          formatter = logging.Formatter('Python: { "loggerName":"%(name)s", "asciTime":"%(asctime)s", "pathName":"%(pathname)s", "logRecordCreationTime":"%(created)f", "functionName":"%(funcName)s", "levelNo":"%(levelno)s", "lineNo":"%(lineno)d", "time":"%(msecs)d", "levelName":"%(levelname)s", "message":"%(message)s"}')

          if any([all([address, port]), filename]):

              #add handler to the logger
              if all([address, port]):
                  remotehandler = logging.handlers.SysLogHandler(address = (address,port))
                  remotehandler.formatter = formatter
                  logger.addHandler(remotehandler)

              if filename is not None:
                  filehandler = logging.FileHandler(filename)
                  filehandler.formatter = formatter
                  logger.addHandler(filehandler)

          else:
              MAX_SIZE = 1024*1024
              LOG_PATH = "/tmp/ztp_python.log"
              handler = logging.handlers.RotatingFileHandler(LOG_PATH, maxBytes=MAX_SIZE, backupCount=1)
              handler.formatter = formatter
              logger.addHandler(handler)

          self.syslogger = logger


    def xrcmd(self, cmd=None):
        """Issue an IOS-XR exec command and obtain the output
           :param cmd: Dictionary representing the XR exec cmd
                       and response to potential prompts
                       { 'exec_cmd': '', 'prompt_response': '' }

           :type cmd: dict            
           :return: Return a dictionary with status and output
                    { 'status': 'error/success', 'output': '' }
           :rtype: dict
        """

        if cmd is None:
            return {"status" : "error", "output" : "No command specified"}

        if not isinstance(cmd, dict):
            return {"status" : "error", "output" : "Dictionary expected as cmd argument, see method documentation"}

        status = "success" 

        if "prompt_response" not in cmd:
            cmd["prompt_response"] = ""

        if self.debug:
            self.logger.debug("Received exec command request: \"%s\"" % cmd["exec_cmd"])
            self.logger.debug("Response to any expected prompt \"%s\"" % cmd["prompt_response"])


        cmd = "source /pkg/bin/ztp_helper.sh && echo -ne \""+cmd["prompt_response"]+" \" | xrcmd " + "\"" + cmd["exec_cmd"] + "\""

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
                if "% Invalid input detected at '^' marker." in fixed_line:
                    status = "error" 
                output = filter(None, output_list)    # Removing empty items

        if self.debug:
            self.logger.debug("Exec command output is %s" % output)
 
        return {"status" : status, "output" : output}



    def xrapply(self, filename=None, reason=None):
        """Apply Configuration to XR using a file 
          
           :param file: Filepath for a config file
                        with the following structure: 

                        !
                        XR config command
                        !
                        end
           
           :param reason: Reason for the config commit.
                          Will show up in the output of:
                          "show configuration commit list detail"
           :type filename: str
           :type reason: str
           :return: Dictionary specifying the effect of the config change
                     { 'status' : 'error/success', 'output': 'exec command based on status'}
                     In case of Error:  'output' = 'show configuration failed' 
                     In case of Success: 'output' = 'show configuration commit changes last 1'
           :rtype: dict 
        """


        if filename is None:
            return {"status" : "error", "output": "No config file provided for xrapply"}

        status = "success"

        try:
            if self.debug:        
                with open(filename, 'r') as config_file:
                    data=config_file.read()
                self.logger.debug("Config File content to be applied %s" % data) 
        except Exception as e:
            return {"status" : "error" , "output" : "Invalid config file provided"}

        if reason is not None:
            cmd = "source /pkg/bin/ztp_helper.sh && xrapply_with_reason \"" + str(reason) + "\" " + filename 
        else:
            cmd = "source /pkg/bin/ztp_helper.sh && xrapply " + filename 

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        out, err = process.communicate()

        # Check if the commit failed

        if process.returncode:
            ## Config commit failed.
            status = "error"
            exec_cmd = "show configuration failed"
            config_failed = self.xrcmd({"exec_cmd": exec_cmd})
            if config_failed["status"] == "error":
                output = "Failed to fetch config failed output"
            else:
                output = config_failed["output"]

            if self.debug:
                self.logger.debug("Config apply through file failed, output = %s" % output)
            return  {"status": status, "output": output}
        else:
            ## Config commit successful. Let's return the last config change
            exec_cmd = "show configuration commit changes last 1"
            config_change = self.xrcmd({"exec_cmd": exec_cmd})
            if config_change["status"] == "error":
                output = "Failed to fetch last config change"
            else:
                output = config_change["output"]

            if self.debug:
                self.logger.debug("Config apply through file successful, last change = %s" % output) 
            return {"status": status, "output" : output}



    def xrapply_string(self, cmd=None, reason=None):

        """Apply Configuration to XR using  a single line string

           :param cmd: Single line string representing an XR config command  
           :param reason: Reason for the config commit.
                          Will show up in the output of:
                          "show configuration commit list detail"
           :type cmd: str
           :type reason: str 
           :return: Dictionary specifying the effect of the config change
                     { 'status' : 'error/success', 'output': 'exec command based on status'}
                     In case of Error:  'output' = 'show configuration failed'
                     In case of Success: 'output' = 'show configuration commit changes last 1'
           :rtype: dict
        """

        if cmd is None:
            return {"status" : "error", "output" : "Config command not specified"}

        status = "success" 

        if self.debug:
            self.logger.debug("Config string to be applied: %s" % cmd)    

        if reason is not None:
            cmd = "source /pkg/bin/ztp_helper.sh && xrapply_string_with_reason \"" + str(reason) + "\" \"" + str(cmd) +  "\""            
        else:
            cmd = "source /pkg/bin/ztp_helper.sh && xrapply_string \"" + str(cmd) + "\""

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        out, err = process.communicate()
      

        if process.returncode:
            ## Config commit failed.
            status = "error"
            exec_cmd = "show configuration failed"
            config_failed = self.xrcmd({"exec_cmd": exec_cmd})
            if config_failed["status"] == "error":
                output = "Failed to fetch config failed output"
            else:
                output = config_failed["output"]
            if self.debug:
                self.logger.debug("Config apply for config string failed, output = %s" % output)
            return  {"status": status, "output": output}

        else:
            ## Config commit successful. Let's return the last config change
            exec_cmd = "show configuration commit changes last 1"
            config_change = self.xrcmd({"exec_cmd": exec_cmd})
            if config_change["status"] == "error":
                output = "Failed to fetch last config change"
            else:
                output = config_change["output"]

            if self.debug:
                self.logger.debug("Config apply for string successful, last change = %s" % output)
            return {"status": status, "output" : output}


    def xrreplace(self, filename=None):
        """Replace XR Configuration using a file 
          
           :param file: Filepath for a config file
                        with the following structure: 

                        !
                        XR config commands
                        !
                        end
           :type filename: str
           :return: Dictionary specifying the effect of the config change
                     { 'status' : 'error/success', 'output': 'exec command based on status'}
                     In case of Error:  'output' = 'show configuration failed' 
                     In case of Success: 'output' = 'show configuration commit changes last 1'
           :rtype: dict 
        """


        if filename is None:
            return {"status" : "error", "output": "No config file provided for xrreplace"}

        status = "success"

        try:
            if self.debug:
                with open(filename, 'r') as config_file:
                    data=config_file.read()
                self.logger.debug("Config File content to be applied %s" % data)
        except Exception as e:
            return {"status" : "error" , "output" : "Invalid config file provided"}

        cmd = "source /pkg/bin/ztp_helper.sh && xrreplace " + filename

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        out, err = process.communicate()

        # Check if the commit failed

        if process.returncode:
            ## Config commit failed.
            status = "error"
            exec_cmd = "show configuration failed"
            config_failed = self.xrcmd({"exec_cmd": exec_cmd})
            if config_failed["status"] == "error":
                output = "Failed to fetch config failed output"
            else:
                output = config_failed["output"]

            if self.debug:
                self.logger.debug("Config replace through file failed, output = %s" % output)
            return  {"status": status, "output": output}
        else:
            ## Config commit successful. Let's return the last config change
            exec_cmd = "show configuration commit changes last 1"
            config_change = self.xrcmd({"exec_cmd": exec_cmd})
            if config_change["status"] == "error":
                output = "Failed to fetch last config change"
            else:
                output = config_change["output"]

            if self.debug:
                self.logger.debug("Config replace through file successful, last change = %s" % output)
            return {"status": status, "output" : output}
