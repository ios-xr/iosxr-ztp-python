#! /usr/bin/env python

import re,os
import json

import sys
sys.path.append("/pkg/bin")
from ztp_helper import ZtpHelpers
from ztp_netconf import *

SAMPLE_CFG='''<edit-config>
 <target>
   <candidate/>
 </target>
 <config>
    <lldp xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ethernet-lldp-cfg">
      <holdtime>60</holdtime>
      <timer>15</timer>
      <enable>true</enable>
    </lldp>
  </config>
 </edit-config>
'''

GET_CFG='''<get-config>
        <source>
            <running/>
        </source>
    </get-config>
'''


class ZtpNcHelper(ZtpHelpers):
    chunk = re.compile('(\n#+\\d+\n)')
    rpc_pipe_err = """
        <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <rpc-error>
            <error-type>transport</error-type>
            <error-tag>resource-denied</error-tag>
            <error-severity>error</error-severity>
            <error-message>No pipe data returned</error-message>
        </rpc-error>
        </rpc-reply>"""

    def xr_netconf(self, request=None):
        nc_handle = xr_netconf(request=request)
        if ( nc_handle is None 
             or  (nc_handle is not None 
                  and not nc_handle.connected)):
            self.syslogger.info("ERROR: Failed to connect to netconf agent!")
            return {"status" : "error", "output": "", "error" : "Failed to connect to netconf agent"} 
        else:
            self.netconf.nc_handle = nc_handle
            return {"status" : "success", "output": self.get_nc_reply(nc_handle.reply), "error" : ""} 


    def get_nc_reply(self, buf=None):
        if not buf:
            self.syslogger.info("Nothing to process")
            return self.rpc_pipe_err 
        else:
            buf=buf.strip() 
            if buf.endswith('\n##'):
                buf = buf[:-3]
            buf = buf[buf.find('<'):]
            reply = re.sub(self.chunk, '', buf)
            return reply


if __name__ == "__main__":

    ztp_obj = ZtpNcHelper()
    # Starts the Netconf Proxy client (without opening up a netconf/ssh port)
    # The first time this clientInit is issued, the netconf server will also 
    # be started which might take time. Subsequent clientInits are much faster 
    ztp_obj.netconf.clientInit()

    # Fetch the running config

    get_config = ztp_obj.xr_netconf(request=GET_CFG)
    if get_config["status"] == "error":
        sys.exit(0)


    print("###################### Netconf response: Current running configuration #######################")
    print(get_config["output"])


    # Configure CDP settings
    lldp_config = ztp_obj.xr_netconf(request=SAMPLE_CFG)
    if lldp_config["status"] == "error":
        sys.exit(0)

    print("###################### Netconf response for LLDP config request #####################") 
    print(lldp_config["output"])


    # Mix netconf operations with CLI operations if you want
    last_config_commit = ztp_obj.xrcmd({"exec_cmd" : "show configuration commit changes last 1"})
  
    if last_config_commit["status"] == "error":
        sys.exit(0)

    print("###################### Last Committed configuration #######################")
    print(last_config_commit["output"]) 
    # Closes the netconf proxy client
    ztp_obj.netconf.clientClose()
