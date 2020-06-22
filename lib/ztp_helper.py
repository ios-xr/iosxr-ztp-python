#!/usr/bin/env python
"""
   author: akshshar@cisco.com
           venkatg@cisco.com
           arhashem@cisco.com

   ztp_helper.py

   ZTP helper for Python

   Copyright (c) 2017-2019 by cisco Systems, Inc.
   All rights reserved.

 """

import os, sys, subprocess, hashlib
import logging, logging.handlers, re
from urllib2 import Request, urlopen, URLError, HTTPError
import urlparse, posixpath, time, json, ssl
from ctypes import cdll
from ztp_netconf import *

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
        self.syslog_server = syslog_server
        try:
            self.syslog_port = int(syslog_port)
        except:
            self.syslog_port = None
        self.syslog_file = syslog_file
        self.setup_syslog()
        self.setup_debug_logger()
        self.debug = False

        #initialize netconf related variables
        self.netconf = self.ZtpNetconfHelper(self.logger)

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
        if not len(logger.handlers):
            logger.setLevel(logging.DEBUG)
            # create console handler and set level to debug
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            logger.addHandler(ch)

        self.logger = logger

    def read_in_chunks(self, file_object, chunk_size):
        """generator to read the file in chunks
           :param file_object: File to be read
           :param chunk_size: Chunk size to read in every iteration
           :type file_object: int
           :type chunk_size: int
        """
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data

    def download_file(self,
                      file_url,
                      destination_folder,
                      md5sum=None,
                      chunk_size=1048576,
                      ca_cert=None,
                      validate_server=True):
        """Download a file from the specified URL
           :param file_url: Complete URL to download file
           :param destination_folder: Folder to store the
                                      downloaded file
           :param md5sum: md5sum of file_url
           :param chunk_size: Chunk size to be read in every read() call
           :param ca_cert: Certificate file used to validate in case of https
           :param validate_server: Validate https transactions
           :type file_url: str
           :type destination_folder: str
           :type md5sum: str
           :type chunk_size: int
           :type ca_cert: str
           :type validate_server: bool
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

            ctx = None
            if urlparse.urlparse(file_url).scheme == 'https':
                if validate_server:
                    if not ca_cert:
                        if self.debug:
                            self.logger.debug("Certificate not provided to validate server")
                        self.syslogger.info("Certificate not provided to validate server")
                        return {"status": "error"}

                    ctx = ssl.create_default_context(cafile=ca_cert)

                else:
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE

            #create the url and the request
            req = Request(file_url)

            hash_md5 = hashlib.md5()

            # Open the url
            try:
                f = urlopen(req, context=ctx)
                self.syslogger.info(
                    "Downloading file %s from URL:%s" % (filename, file_url))

                if self.debug:
                    self.logger.debug("Downloading file %s from URL:%s" %
                                      (filename, file_url))

                # Open our local file for writing
                destination_path = os.path.join(destination_folder, filename)

                with open(destination_path, "w") as local_file:
                    for chunk in self.read_in_chunks(f, chunk_size):
                        local_file.write(chunk)
                        hash_md5.update(chunk)

                md5sum_local = hash_md5.hexdigest()

                if md5sum:
                    self.syslogger.info(
                        "MD5 Sum of the downloaded file is: %s" % md5sum_local)
                    self.syslogger.info(
                        "MD5 Sum of the remote file is: %s" % md5sum)

                    if self.debug:
                        self.logger.debug(
                            "MD5 Sum of the downloaded file is: %s" %
                            md5sum_local)
                        self.logger.debug(
                            "MD5 Sum of the remote file is: %s" % md5sum)

                    if md5sum != md5sum_local:
                        if self.debug:
                            self.logger.debug(
                                "MD5sums of downloaded file and remote file didn't match"
                            )

                        self.syslogger.info(
                            "MD5sums of downloaded file and remote file didn't match"
                        )

                        return {"status": "error"}

                    else:
                        if self.debug:
                            self.logger.debug(
                                "MD5sums of downloaded file and remote file matched"
                            )

                        self.syslogger.info(
                            "MD5sums of downloaded file and remote file matched"
                        )

            #handle errors
            except HTTPError as e:
                if self.debug:
                    self.logger.debug("HTTP Error: %s, %s" % (e.code, file_url))

                self.syslogger.info("HTTP Error: %s, %s" % (e.code, file_url))

                return {"status": "error"}

            except URLError as e:
                if self.debug:
                    self.logger.debug(
                        "URL Error: %s, %s" % (e.reason, file_url))

                self.syslogger.info("URL Error: %s, %s" % (e.reason, file_url))
                return {"status": "error"}

            except Exception as e:
                if self.debug:
                    self.logger.debug(
                        "Exception caught while downloading the file: %s" %
                        (str(e)))

                self.syslogger.info(
                    "Exception caught while downloading the file: %s" %
                    (str(e)))

        return {
            "status": "success",
            "filename": filename,
            "folder": destination_folder
        }

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

            formatter = logging.Formatter(
                'Python: { "loggerName":"%(name)s", "asciTime":"%(asctime)s", "pathName":"%(pathname)s", "logRecordCreationTime":"%(created)f", "functionName":"%(funcName)s", "levelNo":"%(levelno)s", "lineNo":"%(lineno)d", "time":"%(msecs)d", "levelName":"%(levelname)s", "message":"%(message)s"}'
            )

            if any([all([address, port]), filename]):

                #add handler to the logger
                if all([address, port]):
                    remotehandler = logging.handlers.SysLogHandler(
                        address=(address, port))
                    remotehandler.formatter = formatter
                    logger.addHandler(remotehandler)

                if filename is not None:
                    filehandler = logging.FileHandler(filename)
                    filehandler.formatter = formatter
                    logger.addHandler(filehandler)

            else:
                MAX_SIZE = 1024 * 1024
                LOG_PATH = "/tmp/ztp_python.log"
                handler = logging.handlers.RotatingFileHandler(
                    LOG_PATH, maxBytes=MAX_SIZE, backupCount=1)
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
            return {"status": "error", "output": "No command specified"}

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
                "Received exec command request: \"%s\"" % cmd["exec_cmd"])
            self.logger.debug("Response to any expected prompt \"%s\"" %
                              cmd["prompt_response"])

        cmd = "source /pkg/bin/ztp_helper.sh && echo -ne \"" + cmd[
            "prompt_response"] + " \" | xrcmd " + "\"" + cmd["exec_cmd"] + "\""

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        out, err = process.communicate()

        if process.returncode:
            status = "error"
            output = "Failed to get command output"
        else:
            output_list = []
            output = ""

            for line in out.splitlines():
                fixed_line = line.replace("\n", " ").strip()
                output_list.append(fixed_line)
                if "% Invalid input detected at '^' marker." in fixed_line:
                    status = "error"
                output = filter(None, output_list)  # Removing empty items

        if self.debug:
            self.logger.debug("Exec command output is %s" % output)

        return {"status": status, "output": output}

    def admincmd(self, cmd=None):
        """Issue an IOS-XR admin cli command and obtain the output
            :param cmd: Dictionary representing the XR exec cmd
		       and response to potential prompts
		       { 'exec_cmd': '', 'prompt_response': '' }

	   :type cmd: dict
	   :return: Return a dictionary with status and output
		    { 'status': 'error/success', 'output': '' }
	   :rtype: dict
	"""

        if cmd is None:
            return {"status": "error", "output": "No command specified"}

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
                "Received admin command request: \"%s\"" % cmd["exec_cmd"])
            self.logger.debug("Response to any expected prompt \"%s\"" %
                              cmd["prompt_response"])

        cmd = "source /pkg/bin/ztp_helper.sh && echo -ne \"" + cmd[
            "prompt_response"] + " \" | admincmd " + "\"" + cmd[
                "exec_cmd"] + "\""

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        out, err = process.communicate()

        if process.returncode:
            status = "error"
            output = "Failed to get command output"
        else:
            output_list = []
            output = ""

            for line in out.splitlines():
                fixed_line = line.replace("\n", " ").strip()
                output_list.append(fixed_line)
                if "% Invalid input detected at '^' marker." in fixed_line:
                    status = "error"
                output = filter(None, output_list)  # Removing empty items

        if self.debug:
            self.logger.debug("Admin command output is %s" % output)

        return {"status": status, "output": output}

    def xrapply(self, filename=None, reason=None, extra_auth=False, atomic=False):
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
           :param extra_auth: Execute command with extra authentication
           :type filename: str
           :type reason: str
           :type extra_auth: bool
           :return: Dictionary specifying the effect of the config change
                     { 'status' : 'error/success', 'output': 'exec command based on status'}
                     In case of Error:  'output' = 'show configuration failed'
                     In case of Success: 'output' = 'show configuration commit changes last 1'
           :rtype: dict
        """

        if filename is None:
            return {
                "status": "error",
                "output": "No config file provided for xrapply"
            }

        status = "success"

        try:
            if self.debug:
                with open(filename, 'r') as config_file:
                    data = config_file.read()
                self.logger.debug("Config File content to be applied %s" % data)
        except Exception as e:
            return {"status": "error", "output": "Invalid config file provided"}

        if reason is not None:
            cmd = "source /pkg/bin/ztp_helper.sh && xrapply_with_reason \"" + str(
                reason) + "\" " + filename
            if atomic:
                cmd += " " + "atomic"
        elif extra_auth:
            cmd = "source /pkg/bin/ztp_helper.sh && xrapply_with_extra_auth " + filename
        elif atomic:
            cmd = "source /pkg/bin/ztp_helper.sh && xrapply " + filename + " " + "atomic"
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
                self.logger.debug(
                    "Config apply through file failed, output = %s" % output)
            return {"status": status, "output": output}
        else:
            ## Config commit successful. Let's return the last config change
            exec_cmd = "show configuration commit changes last 1"
            config_change = self.xrcmd({"exec_cmd": exec_cmd})
            if config_change["status"] == "error":
                output = "Failed to fetch last config change"
            else:
                output = config_change["output"]

            if self.debug:
                self.logger.debug(
                    "Config apply through file successful, last change = %s" %
                    output)
            return {"status": status, "output": output}

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
            return {"status": "error", "output": "Config command not specified"}

        status = "success"

        if self.debug:
            self.logger.debug("Config string to be applied: %s" % cmd)

        if reason is not None:
            cmd = "source /pkg/bin/ztp_helper.sh && xrapply_string_with_reason \"" + reason + "\" \"" + cmd + "\""
        else:
            cmd = "source /pkg/bin/ztp_helper.sh && xrapply_string \"" + cmd + "\""

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
                self.logger.debug(
                    "Config apply for config string failed, output = %s" %
                    output)
            return {"status": status, "output": output}

        else:
            ## Config commit successful. Let's return the last config change
            exec_cmd = "show configuration commit changes last 1"
            config_change = self.xrcmd({"exec_cmd": exec_cmd})
            if config_change["status"] == "error":
                output = "Failed to fetch last config change"
            else:
                output = config_change["output"]

            if self.debug:
                self.logger.debug(
                    "Config apply for string successful, last change = %s" %
                    output)
            return {"status": status, "output": output}

    def xrreplace(self, filename=None, extra_auth=False):
        """Replace XR Configuration using a file

           :param file: Filepath for a config file
                        with the following structure:

                        !
                        XR config commands
                        !
                        end
           :param extra_auth: Execute command with extra authentication
           :type filename: str
           :type extra_auth: bool
           :return: Dictionary specifying the effect of the config change
                     { 'status' : 'error/success', 'output': 'exec command based on status'}
                     In case of Error:  'output' = 'show configuration failed'
                     In case of Success: 'output' = 'show configuration commit changes last 1'
           :rtype: dict
        """

        if filename is None:
            return {
                "status": "error",
                "output": "No config file provided for xrreplace"
            }

        status = "success"

        try:
            if self.debug:
                with open(filename, 'r') as config_file:
                    data = config_file.read()
                self.logger.debug("Config File content to be applied %s" % data)
        except Exception as e:
            return {"status": "error", "output": "Invalid config file provided"}

        if extra_auth:
            cmd = "source /pkg/bin/ztp_helper.sh && xrreplace_with_extra_auth " + filename
        else:
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
                self.logger.debug(
                    "Config replace through file failed, output = %s" % output)
            return {"status": status, "output": output}
        else:
            ## Config commit successful. Let's return the last config change
            exec_cmd = "show configuration commit changes last 1"
            config_change = self.xrcmd({"exec_cmd": exec_cmd})
            if config_change["status"] == "error":
                output = "Failed to fetch last config change"
            else:
                output = config_change["output"]

            if self.debug:
                self.logger.debug(
                    "Config replace through file successful, last change = %s" %
                    output)
            return {"status": status, "output": output}

    def operns_if_name_to_xrnns(self, ifName, sysdb=False):
        """Convert interface name from operns to xrnns format
            e.g. Gi0_0_0_0 to GigabitEthernet0/0/0/0

           :param name: Interface name
           :param sysdb: For converting to Sysdb path
                         e.g. Gi0_0_0_0 to GigabitEthernet0_0_0_0

           :type name: str
           :type sysdb: bool

           :return: String converted to xrnns format
           :rtype: str
        """
        if not sysdb:
            ifName = ifName.replace('_', '/')

        ifName = ifName.replace('Gi', 'GigabitEthernet')
        ifName = ifName.replace('Tg', 'TenGigE')
        ifName = ifName.replace('Fg', 'FortyGigE')
        ifName = ifName.replace('Tf', 'TwentyFiveGigE')
        ifName = ifName.replace('Hu', 'HundredGigE')
        ifName = ifName.replace('Hg', 'HundredGigE')
        ifName = ifName.replace('FH', 'FourHundredGigE')
        ifName = ifName.replace('Mg', 'MgmtEth')

        return ifName

    def ztp_release_dhcp_ip(self):
        """Release IP address that ZTP has allocated from DHCP server

	   :return: Return a dictionary with status and output
		    { 'status': 'error/success', 'output': '' }
           :rtype: dict
        """

        cmd = "source /pkg/bin/ztp_helper.sh && ztp_release_dhcp_ip"

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        out, err = process.communicate()

        # Check if the release failed
        if process.returncode:
            ## Release failed.
            status = "error"
            output = "Failed to release dhcp IP address"
            if self.debug:
                self.logger.debug("Error releasing dhcp IP address")
        else:
            ## Release successful.
            status = "success"
            output = ""
            if self.debug:
                self.logger.debug("Done releasing dhcp IP address")

        return {"status": status, "output": output}

    def ztp_enable(self):
        """
        Enables ZTP
        :return: Return a dictionary with status and output
                    { 'status': 'error/success', 'output': '' }
        :rtype: dict
        """
        return self.xrcmd({'exec_cmd': 'ztp enable noprompt'})

    def ztp_disable(self):
        """
        Disables ZTP
        :return: Return a dictionary with status and output
                    { 'status': 'error/success', 'output': '' }
        :rtype: dict
        """
        return self.xrcmd({'exec_cmd': 'ztp disable noprompt'})


    class ZtpNetconfHelper(object):  # Child object, member of ZtpHelpers
        def __init__(self, logger, nc_handle=None):
            # logger init
            self.logger = logger
            # Store Client Handle For Reuse
            self.nc_handle = nc_handle

        def clientInit(self):
            """
               Initiate netconf session
               :This api will apply netconf-yang agent ssh in the config mode
                        !
                        netconf-yang agent
                         ssh
                        !
                        end
               :rtype: True on success
            """
            retry_count = 1
            self.configFile = "/tmp/nf.cfg"
            self.ztpHelpers = ZtpHelpers()

            try:
               with open(self.configFile, 'w') as fio:
                  fio.write("netconf-yang agent ssh")
                  fio.close()
            except IOError:
               self.logger.debug("Failed to write config to a file")
               return False

            self.logger.debug("netconf init attempt: %s" % retry_count)
            ret = self.ztpHelpers.xrapply(self.configFile)
            while ((ret['status'] is 'error') and (retry_count <= 3)):
                self.logger.debug("netconf init attempt: %s" % retry_count)
                ret = self.ztpHelpers.xrapply(self.configFile)
                retry_count += 1

            os.remove(self.configFile)
            if (ret['status'] is 'error' and retry_count == 3):
                return False

            tries = 12
            procStatus = False
            for i in range(tries):
               proc = subprocess.Popen("ip netns exec xrnns /pkg/bin/show_netconf_agent status | grep state | grep ready", stdout=subprocess.PIPE, shell=True)
               (out, err) = proc.communicate()
               out = out.decode().strip().split()[-1] if out else ''
               if out.strip() == "ready":
                  procStatus = True
                  break
               else:
                  time.sleep(5)
            if not procStatus:
               self.logger.debug("Netconf yang agent failed to come up")
               return False
            self.logger.debug("Netconf yang agent is up")
            return True

        def clientOperate(self, log, request, response):
            """
               API to perform netconf operation
               :param request: netconf request to apply
                      respone: response from the netconf server
               :rtype: nc_handle not None on success
            """
            self.ztpHelpers = ZtpHelpers()
            if request is None:
                return {
                    "status": "error",
                    "output": "request is empty or errored"
                }
            status = "success"

            if request.lstrip()[:4] == "http":
                urlexp = re.compile(
                    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
                )
                if urlexp.search(request.lstrip()):
                    # Handle file from remote server
                    rc = self.ztpHelpers.download_file(
                        request, destination_folder="/tmp/")
                    if rc["status"] == "error":
                        self.logger.debug(
                            "File download failed for Netconf Operation, Abort!"
                        )
                        return False
                    self.logger.debug("Config File download successful")
                    filePath = rc["folder"] + rc["filename"]
                    with open(filePath, 'r') as configFile:
                        data = configFile.read()
                else:
                    self.logger.debug(
                        "Wrongly formatted url. Should start with http://..")
            else:
                data = request

            nc_handle = xr_netconf(log, data, response)
            if nc_handle:
                self.nc_handle = nc_handle
            self.logger.debug("Netconf operation successfull")
            return nc_handle

        def clientClose(self):
            """
               API to close a netconf proxy session
               :rtype: True on success
            """
            nc_handle = self.nc_handle
            rc = xr_netconf_proxy_stop(nc_handle)
            if (rc is True):
                self.logger.debug("Netconf session closed")
            else:
                self.logger.debug("Failed to close Netconf session")
            return rc
