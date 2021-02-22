# Output Runs

## Sample run on NCS5501 for simple_ztp_netconf.py

```
[NCS5501:~]$ python ztp_netconf_test.py
# netconf_client_ztp_lib - version 1.2 #
2021-02-22 13:53:11,587 - DebugZTPLogger - DEBUG - netconf init attempt: 1
Building configuration...
2021-02-22 13:53:18,117 - DebugZTPLogger - DEBUG - Netconf yang agent is up
###################### Netconf response: Current running configuration #######################
<?xml version="1.0"?>
<rpc-reply message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
 <data>
  <ssh xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-crypto-ssh-cfg">
   <server>
    <v2></v2>
   </server>
  </ssh>
  <lldp xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ethernet-lldp-cfg">
   <timer>15</timer>
   <enable>true</enable>
   <holdtime>60</holdtime>
  </lldp>
  <l2vpn xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-l2vpn-cfg">
   <enable></enable>
   <database>
    <bridge-domain-groups>
     <bridge-domain-group>
      <name>Test</name>
      <bridge-domains>
       <bridge-domain>
        <name>Test</name>
        <bd-attachment-circuits>
         <bd-attachment-circuit>
          <name>HundredGigE0/0/1/0.100</name>
         </bd-attachment-circuit>
        </bd-attachment-circuits>
        <routed-interfaces>
         <routed-interface>
          <interface-name>BVI100</interface-name>
         </routed-interface>
        </routed-interfaces>
       </bridge-domain>
      </bridge-domains>
     </bridge-domain-group>
    </bridge-domain-groups>
   </database>
  </l2vpn>
  <tpa xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-kim-tpa-cfg">
   <vrf-names>
    <vrf-name>
     <vrf-name>blue</vrf-name>
    </vrf-name>
    <vrf-name>
     <vrf-name>mgmt</vrf-name>
     <address-family>
      <ipv4>
       <default-route>mgmt</default-route>
      </ipv4>
     </address-family>
    </vrf-name>
   </vrf-names>
  </tpa>
  <aaa xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-aaa-lib-cfg">
   <usernames xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-aaa-locald-cfg">
    <username>
     <ordering-index>0</ordering-index>
     <name>cisco</name>
     <usergroup-under-usernames>
      <usergroup-under-username>
       <name>root-lr</name>
      </usergroup-under-username>
      <usergroup-under-username>
       <name>cisco-support</name>
      </usergroup-under-username>
     </usergroup-under-usernames>
     <secret>
      <type>type10</type>
      <secret10>$6$jU4bp0clNhQK9p0.$uAnbzURjWcZMKcnJG5DRRDbB0kXfRDZke.fSmWBkVNJO4tx.oKWAzhLClPL6AinDsXv3PqaQw8fNCUaDJVVpf/</secret10>
     </secret>
    </username>
    <username>
     <ordering-index>1</ordering-index>
     <name>root</name>
     <usergroup-under-usernames>
      <usergroup-under-username>
       <name>root-lr</name>
      </usergroup-under-username>
     </usergroup-under-usernames>
     <password>13091610</password>
    </username>
   </usernames>
  </aaa>
  <call-home xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-call-home-cfg">
   <active></active>
   <contact-smart-licensing>true</contact-smart-licensing>
   <profiles>
    <profile>
     <profile-name>CiscoTAC-1</profile-name>
     <active></active>
     <methods>
      <method>
       <method>email</method>
       <enable>false</enable>
      </method>
      <method>
       <method>http</method>
       <enable>true</enable>
      </method>
     </methods>
    </profile>
   </profiles>
  </call-home>
  <snmp xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-snmp-agent-cfg">
   <administration>
    <default-communities>
     <default-community>
      <community-name>cisco</community-name>
      <priviledge>read-write</priviledge>
     </default-community>
    </default-communities>
   </administration>
  </snmp>
  <isis xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-clns-isis-cfg">
   <instances>
    <instance>
     <instance-name>test</instance-name>
     <running></running>
     <is-type>level2</is-type>
     <nets>
      <net>
       <net-name>47.0004.004d.0001.0001.0c11.1110.00</net-name>
      </net>
     </nets>
    </instance>
   </instances>
  </isis>
  <mpls-lsd xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-mpls-lsd-cfg">
   <label-databases>
    <label-database>
     <label-database-id>0</label-database-id>
     <label-range>
      <minvalue>34000</minvalue>
      <max-value>749999</max-value>
      <min-static-value>34000</min-static-value>
      <max-static-value>99999</max-static-value>
     </label-range>
     <label-blocks>
      <label-block>
       <block-name>SWAN_CBF</block-name>
       <block-type>cbf</block-type>
       <range-type>lower-upper</range-type>
       <lower-bound>24000</lower-bound>
       <upper-bound>33999</upper-bound>
       <block-size>0</block-size>
       <client-instance-name>swanagent</client-instance-name>
      </label-block>
     </label-blocks>
    </label-database>
   </label-databases>
  </mpls-lsd>
  <netconf-yang xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-man-netconf-cfg">
   <agent>
    <ssh>
     <enable></enable>
    </ssh>
   </agent>
  </netconf-yang>
  <host-names xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-shellutil-cfg">
   <host-name>NCS5501</host-name>
  </host-names>
  <grpc xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-man-ems-cfg">
   <port>57777</port>
   <enable></enable>
   <address-family>ipv4</address-family>
   <service-layer>
    <enable></enable>
   </service-layer>
  </grpc>
  <vrfs xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-infra-rsi-cfg">
   <vrf>
    <vrf-name>blue</vrf-name>
    <create></create>
   </vrf>
   <vrf>
    <vrf-name>mgmt</vrf-name>
    <create></create>
   </vrf>
  </vrfs>
  <interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
   <interface-configuration>
    <active>act</active>
    <interface-name>BVI100</interface-name>
    <interface-virtual></interface-virtual>
    <ipv4-network xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
     <addresses>
      <primary>
       <address>12.1.1.20</address>
       <netmask>255.255.255.0</netmask>
      </primary>
     </addresses>
    </ipv4-network>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>Loopback99</interface-name>
    <interface-virtual></interface-virtual>
    <ipv4-network xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
     <addresses>
      <primary>
       <address>1.1.1.1</address>
       <netmask>255.255.255.255</netmask>
      </primary>
     </addresses>
    </ipv4-network>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/1</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/2</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/4</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/5</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/6</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/7</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/8</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/9</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/10</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/11</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/12</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/13</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/15</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/16</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/17</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/21</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/22</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/23</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/24</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/25</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/26</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/27</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/28</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/29</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/30</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/31</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/32</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/33</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/34</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/35</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/36</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/37</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/38</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/39</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/40</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/41</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/42</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/43</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/44</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/45</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/46</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>TenGigE0/0/0/47</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>HundredGigE0/0/1/0</interface-name>
    <ipv4-network xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
     <addresses>
      <primary>
       <address>11.1.1.20</address>
       <netmask>255.255.255.0</netmask>
      </primary>
     </addresses>
    </ipv4-network>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>HundredGigE0/0/1/1</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>HundredGigE0/0/1/2</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>HundredGigE0/0/1/3</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>HundredGigE0/0/1/4</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>HundredGigE0/0/1/5</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>MgmtEth0/RP0/CPU0/0</interface-name>
    <ipv4-network xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
     <addresses>
      <primary>
       <address>192.168.152.21</address>
       <netmask>255.255.255.0</netmask>
      </primary>
     </addresses>
    </ipv4-network>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>GigabitEthernet0/0/0/0</interface-name>
    <ipv4-network xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
     <addresses>
      <primary>
       <address>192.168.153.2</address>
       <netmask>255.255.255.0</netmask>
      </primary>
     </addresses>
    </ipv4-network>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>GigabitEthernet0/0/0/3</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>HundredGigE0/0/1/0.100</interface-name>
    <interface-mode-non-physical>l2-transport</interface-mode-non-physical>
    <ethernet-service xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-l2-eth-infra-cfg">
     <encapsulation>
      <outer-tag-type>match-dot1q</outer-tag-type>
      <outer-range1-low>100</outer-range1-low>
     </encapsulation>
     <rewrite>
      <rewrite-type>pop1</rewrite-type>
     </rewrite>
    </ethernet-service>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>GigabitEthernet0/0/0/14</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>GigabitEthernet0/0/0/18</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>GigabitEthernet0/0/0/19</interface-name>
    <ipv4-network xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
     <addresses>
      <primary>
       <address>10.1.1.10</address>
       <netmask>255.255.255.0</netmask>
      </primary>
     </addresses>
    </ipv4-network>
   </interface-configuration>
   <interface-configuration>
    <active>act</active>
    <interface-name>GigabitEthernet0/0/0/20</interface-name>
    <shutdown></shutdown>
   </interface-configuration>
  </interface-configurations>
  <interfaces xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-um-interface-cfg">
   <interface>
    <interface-name>BVI100</interface-name>
    <ipv4>
     <addresses xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-um-if-ip-address-cfg">
      <address>
       <address>12.1.1.20</address>
       <netmask>255.255.255.0</netmask>
      </address>
     </addresses>
    </ipv4>
   </interface>
   <interface>
    <interface-name>Loopback99</interface-name>
    <ipv4>
     <addresses xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-um-if-ip-address-cfg">
      <address>
       <address>1.1.1.1</address>
       <netmask>255.255.255.255</netmask>
      </address>
     </addresses>
    </ipv4>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/1</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/2</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/4</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/5</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/6</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/7</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/8</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/9</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/10</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/11</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/12</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/13</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/15</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/16</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/17</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/21</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/22</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/23</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/24</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/25</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/26</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/27</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/28</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/29</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/30</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/31</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/32</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/33</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/34</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/35</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/36</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/37</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/38</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/39</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/40</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/41</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/42</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/43</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/44</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/45</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/46</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>TenGigE0/0/0/47</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>HundredGigE0/0/1/0</interface-name>
    <ipv4>
     <addresses xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-um-if-ip-address-cfg">
      <address>
       <address>11.1.1.20</address>
       <netmask>255.255.255.0</netmask>
      </address>
     </addresses>
    </ipv4>
   </interface>
   <interface>
    <interface-name>HundredGigE0/0/1/1</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>HundredGigE0/0/1/2</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>HundredGigE0/0/1/3</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>HundredGigE0/0/1/4</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>HundredGigE0/0/1/5</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>MgmtEth0/RP0/CPU0/0</interface-name>
    <ipv4>
     <addresses xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-um-if-ip-address-cfg">
      <address>
       <address>192.168.152.21</address>
       <netmask>255.255.255.0</netmask>
      </address>
     </addresses>
    </ipv4>
   </interface>
   <interface>
    <interface-name>GigabitEthernet0/0/0/0</interface-name>
    <ipv4>
     <addresses xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-um-if-ip-address-cfg">
      <address>
       <address>192.168.153.2</address>
       <netmask>255.255.255.0</netmask>
      </address>
     </addresses>
    </ipv4>
   </interface>
   <interface>
    <interface-name>GigabitEthernet0/0/0/3</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>HundredGigE0/0/1/0.100</interface-name>
    <sub-interface-type>
     <l2transport/>
    </sub-interface-type>
    <l2transport-encapsulation xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-um-l2-ethernet-cfg">
     <dot1q>
      <vlan-id>100</vlan-id>
     </dot1q>
    </l2transport-encapsulation>
    <rewrite xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-um-l2-ethernet-cfg">
     <ingress>
      <tag>
       <pop>
        <one/>
       </pop>
      </tag>
     </ingress>
    </rewrite>
   </interface>
   <interface>
    <interface-name>GigabitEthernet0/0/0/14</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>GigabitEthernet0/0/0/18</interface-name>
    <shutdown/>
   </interface>
   <interface>
    <interface-name>GigabitEthernet0/0/0/19</interface-name>
    <ipv4>
     <addresses xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-um-if-ip-address-cfg">
      <address>
       <address>10.1.1.10</address>
       <netmask>255.255.255.0</netmask>
      </address>
     </addresses>
    </ipv4>
   </interface>
   <interface>
    <interface-name>GigabitEthernet0/0/0/20</interface-name>
    <shutdown/>
   </interface>
  </interfaces>
  <router xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-um-router-isis-cfg">
   <isis>
    <processes>
     <process>
      <process-id>test</process-id>
      <is-type>level-2-only</is-type>
      <nets>
       <net>
        <net-id>47.0004.004d.0001.0001.0c11.1110.00</net-id>
       </net>
      </nets>
     </process>
    </processes>
   </isis>
  </router>
  <mpls xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-um-mpls-lsd-cfg">
   <label>
    <blocks>
     <block>
      <name>SWAN_CBF</name>
      <type>cbf</type>
      <start>24000</start>
      <end>33999</end>
      <client>swanagent</client>
     </block>
    </blocks>
   </label>
  </mpls>
  <vrfs xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-um-vrf-cfg">
   <vrf>
    <vrf-name>blue</vrf-name>
   </vrf>
   <vrf>
    <vrf-name>mgmt</vrf-name>
   </vrf>
  </vrfs>
  <netconf-yang xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-um-netconf-yang-cfg">
   <agent>
    <ssh/>
   </agent>
  </netconf-yang>
  <grpc xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-um-grpc-cfg">
   <port>57777</port>
   <address-family>
    <ipv4/>
   </address-family>
   <service-layer/>
  </grpc>
  <lldp xmlns="http://openconfig.net/yang/lldp">
   <config>
    <enabled>true</enabled>
    <hello-timer>15</hello-timer>
   </config>
  </lldp>
  <system xmlns="http://openconfig.net/yang/system">
   <ssh-server>
    <config>
     <enable>true</enable>
     <protocol-version>V2</protocol-version>
    </config>
   </ssh-server>
   <aaa>
    <authentication>
     <users>
      <user>
       <username>cisco</username>
       <config>
        <username>cisco</username>
        <role>root-lr</role>
        <password-hashed>$6$jU4bp0clNhQK9p0.$uAnbzURjWcZMKcnJG5DRRDbB0kXfRDZke.fSmWBkVNJO4tx.oKWAzhLClPL6AinDsXv3PqaQw8fNCUaDJVVpf/</password-hashed>
       </config>
      </user>
      <user>
       <username>root</username>
       <config>
        <username>root</username>
        <role>root-lr</role>
        <password>13091610</password>
       </config>
      </user>
     </users>
    </authentication>
   </aaa>
   <config>
    <hostname>NCS5501</hostname>
   </config>
   <grpc-server>
    <config>
     <port>57777</port>
     <enable>true</enable>
    </config>
   </grpc-server>
  </system>
  <network-instances xmlns="http://openconfig.net/yang/network-instance">
   <network-instance>
    <name>default</name>
    <protocols>
     <protocol>
      <identifier xmlns:idx="http://openconfig.net/yang/policy-types">idx:ISIS</identifier>
      <name>test</name>
      <config>
       <identifier xmlns:idx="http://openconfig.net/yang/policy-types">idx:ISIS</identifier>
       <name>test</name>
      </config>
      <isis>
       <global>
        <config>
         <level-capability>LEVEL_2</level-capability>
         <net>47.0004.004d.0001.0001.0c11.1110.00</net>
        </config>
       </global>
      </isis>
     </protocol>
    </protocols>
   </network-instance>
   <network-instance>
    <name>blue</name>
    <config>
     <name>blue</name>
    </config>
   </network-instance>
   <network-instance>
    <name>mgmt</name>
    <config>
     <name>mgmt</name>
    </config>
   </network-instance>
  </network-instances>
  <interfaces xmlns="http://openconfig.net/yang/interfaces">
   <interface>
    <name>BVI100</name>
    <config>
     <name>BVI100</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:propVirtual</type>
    </config>
    <subinterfaces>
     <subinterface>
      <index>0</index>
      <ipv4 xmlns="http://openconfig.net/yang/interfaces/ip">
       <addresses>
        <address>
         <ip>12.1.1.20</ip>
         <config>
          <ip>12.1.1.20</ip>
          <prefix-length>24</prefix-length>
         </config>
        </address>
       </addresses>
      </ipv4>
     </subinterface>
    </subinterfaces>
   </interface>
   <interface>
    <name>Loopback99</name>
    <config>
     <name>Loopback99</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:softwareLoopback</type>
    </config>
    <subinterfaces>
     <subinterface>
      <index>0</index>
      <ipv4 xmlns="http://openconfig.net/yang/interfaces/ip">
       <addresses>
        <address>
         <ip>1.1.1.1</ip>
         <config>
          <ip>1.1.1.1</ip>
          <prefix-length>32</prefix-length>
         </config>
        </address>
       </addresses>
      </ipv4>
     </subinterface>
    </subinterfaces>
   </interface>
   <interface>
    <name>TenGigE0/0/0/1</name>
    <config>
     <name>TenGigE0/0/0/1</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/2</name>
    <config>
     <name>TenGigE0/0/0/2</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/4</name>
    <config>
     <name>TenGigE0/0/0/4</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/5</name>
    <config>
     <name>TenGigE0/0/0/5</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/6</name>
    <config>
     <name>TenGigE0/0/0/6</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/7</name>
    <config>
     <name>TenGigE0/0/0/7</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/8</name>
    <config>
     <name>TenGigE0/0/0/8</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/9</name>
    <config>
     <name>TenGigE0/0/0/9</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/10</name>
    <config>
     <name>TenGigE0/0/0/10</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/11</name>
    <config>
     <name>TenGigE0/0/0/11</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/12</name>
    <config>
     <name>TenGigE0/0/0/12</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/13</name>
    <config>
     <name>TenGigE0/0/0/13</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/15</name>
    <config>
     <name>TenGigE0/0/0/15</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/16</name>
    <config>
     <name>TenGigE0/0/0/16</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/17</name>
    <config>
     <name>TenGigE0/0/0/17</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/21</name>
    <config>
     <name>TenGigE0/0/0/21</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/22</name>
    <config>
     <name>TenGigE0/0/0/22</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/23</name>
    <config>
     <name>TenGigE0/0/0/23</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/24</name>
    <config>
     <name>TenGigE0/0/0/24</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/25</name>
    <config>
     <name>TenGigE0/0/0/25</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/26</name>
    <config>
     <name>TenGigE0/0/0/26</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/27</name>
    <config>
     <name>TenGigE0/0/0/27</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/28</name>
    <config>
     <name>TenGigE0/0/0/28</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/29</name>
    <config>
     <name>TenGigE0/0/0/29</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/30</name>
    <config>
     <name>TenGigE0/0/0/30</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/31</name>
    <config>
     <name>TenGigE0/0/0/31</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/32</name>
    <config>
     <name>TenGigE0/0/0/32</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/33</name>
    <config>
     <name>TenGigE0/0/0/33</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/34</name>
    <config>
     <name>TenGigE0/0/0/34</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/35</name>
    <config>
     <name>TenGigE0/0/0/35</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/36</name>
    <config>
     <name>TenGigE0/0/0/36</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/37</name>
    <config>
     <name>TenGigE0/0/0/37</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/38</name>
    <config>
     <name>TenGigE0/0/0/38</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/39</name>
    <config>
     <name>TenGigE0/0/0/39</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/40</name>
    <config>
     <name>TenGigE0/0/0/40</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/41</name>
    <config>
     <name>TenGigE0/0/0/41</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/42</name>
    <config>
     <name>TenGigE0/0/0/42</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/43</name>
    <config>
     <name>TenGigE0/0/0/43</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/44</name>
    <config>
     <name>TenGigE0/0/0/44</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/45</name>
    <config>
     <name>TenGigE0/0/0/45</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/46</name>
    <config>
     <name>TenGigE0/0/0/46</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>TenGigE0/0/0/47</name>
    <config>
     <name>TenGigE0/0/0/47</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>HundredGigE0/0/1/0</name>
    <config>
     <name>HundredGigE0/0/1/0</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
    <subinterfaces>
     <subinterface>
      <index>0</index>
      <ipv4 xmlns="http://openconfig.net/yang/interfaces/ip">
       <addresses>
        <address>
         <ip>11.1.1.20</ip>
         <config>
          <ip>11.1.1.20</ip>
          <prefix-length>24</prefix-length>
         </config>
        </address>
       </addresses>
      </ipv4>
     </subinterface>
     <subinterface>
      <index>100</index>
      <config>
       <index>100</index>
      </config>
     </subinterface>
    </subinterfaces>
   </interface>
   <interface>
    <name>HundredGigE0/0/1/1</name>
    <config>
     <name>HundredGigE0/0/1/1</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>HundredGigE0/0/1/2</name>
    <config>
     <name>HundredGigE0/0/1/2</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>HundredGigE0/0/1/3</name>
    <config>
     <name>HundredGigE0/0/1/3</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>HundredGigE0/0/1/4</name>
    <config>
     <name>HundredGigE0/0/1/4</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>HundredGigE0/0/1/5</name>
    <config>
     <name>HundredGigE0/0/1/5</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>MgmtEth0/RP0/CPU0/0</name>
    <config>
     <name>MgmtEth0/RP0/CPU0/0</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
    <subinterfaces>
     <subinterface>
      <index>0</index>
      <ipv4 xmlns="http://openconfig.net/yang/interfaces/ip">
       <addresses>
        <address>
         <ip>192.168.152.21</ip>
         <config>
          <ip>192.168.152.21</ip>
          <prefix-length>24</prefix-length>
         </config>
        </address>
       </addresses>
      </ipv4>
     </subinterface>
    </subinterfaces>
   </interface>
   <interface>
    <name>GigabitEthernet0/0/0/0</name>
    <config>
     <name>GigabitEthernet0/0/0/0</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
    <subinterfaces>
     <subinterface>
      <index>0</index>
      <ipv4 xmlns="http://openconfig.net/yang/interfaces/ip">
       <addresses>
        <address>
         <ip>192.168.153.2</ip>
         <config>
          <ip>192.168.153.2</ip>
          <prefix-length>24</prefix-length>
         </config>
        </address>
       </addresses>
      </ipv4>
     </subinterface>
    </subinterfaces>
   </interface>
   <interface>
    <name>GigabitEthernet0/0/0/3</name>
    <config>
     <name>GigabitEthernet0/0/0/3</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>GigabitEthernet0/0/0/14</name>
    <config>
     <name>GigabitEthernet0/0/0/14</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>GigabitEthernet0/0/0/18</name>
    <config>
     <name>GigabitEthernet0/0/0/18</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
   <interface>
    <name>GigabitEthernet0/0/0/19</name>
    <config>
     <name>GigabitEthernet0/0/0/19</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
    <subinterfaces>
     <subinterface>
      <index>0</index>
      <ipv4 xmlns="http://openconfig.net/yang/interfaces/ip">
       <addresses>
        <address>
         <ip>10.1.1.10</ip>
         <config>
          <ip>10.1.1.10</ip>
          <prefix-length>24</prefix-length>
         </config>
        </address>
       </addresses>
      </ipv4>
     </subinterface>
    </subinterfaces>
   </interface>
   <interface>
    <name>GigabitEthernet0/0/0/20</name>
    <config>
     <name>GigabitEthernet0/0/0/20</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:ethernetCsmacd</type>
     <enabled>false</enabled>
    </config>
    <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
     <config>
      <auto-negotiate>false</auto-negotiate>
     </config>
    </ethernet>
   </interface>
  </interfaces>
 </data>
</rpc-reply>

###################### Netconf response for LLDP config request #####################
<?xml version="1.0"?>
<rpc-reply message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
 <ok/>
</rpc-reply>

Building configuration...
###################### Last Committed configuration #######################
['!! IOS XR Configuration 7.3.1.31I', 'lldp', 'timer 15', 'holdtime 60', '!', 'end']
2021-02-22 13:53:21,584 - DebugZTPLogger - DEBUG - Netconf session closed
[NCS5501:~]$ 
[NCS5501:~]$ 


```
