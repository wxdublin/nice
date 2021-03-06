#
# Copyright (c) 2011, EPFL (Ecole Politechnique Federale de Lausanne)
# All rights reserved.
#
# Created by Marco Canini, Daniele Venzano, Dejan Kostic, Jennifer Rexford
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   -  Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#   -  Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#   -  Neither the names of the contributors, nor their associated universities or
#      organizations may be used to endorse or promote products derived from this
#      software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
import abc, copy

import nox.lib.openflow as openflow

import utils

IN_PORT = 'in_port'
AP_SRC = 'ap_src'
AP_DST = 'ap_dst'
DL_SRC = 'dl_src'
DL_DST = 'dl_dst'
DL_VLAN = 'dl_vlan'
DL_VLAN_PCP = 'dl_vlan_pcp'
DL_TYPE = 'dl_type'
NW_SRC = 'nw_src'
NW_SRC_N_WILD = 'nw_src_n_wild'
NW_DST = 'nw_dst'
NW_DST_N_WILD = 'nw_dst_n_wild'
NW_PROTO = 'nw_proto'
NW_TOS = 'nw_tos'
TP_SRC = 'tp_src'
TP_DST = 'tp_dst'
GROUP_SRC = 'group_src'
GROUP_DST = 'group_dst'
N_TABLES = 'n_tables'
N_BUFFERS = 'n_bufs'
CAPABILITES = 'caps'
ACTIONS = 'actions'
PORTS = 'ports'
PORT_NO = 'port_no'
SPEED = 'speed'
CONFIG = 'config'
STATE = 'state'
CURR = 'curr'
ADVERTISED = 'advertised'
SUPPORTED = 'supported'
PEER = 'peer'
HW_ADDR = 'hw_addr'
CONTINUE = 0
STOP = 1

class Component:
    __metaclass__ = abc.ABCMeta

    def __init__(self, ctxt):
        self.ctxt = ctxt
        self.packet_in_cb = None
        self.datapath_leave_cb = None
        self.datapath_join_cb = None
        self.flow_removed_cb = None
        self.port_status_cb = None

    def register_for_port_status(self, func):
        self.port_status_cb = func

    def register_for_packet_in(self, func):
        self.packet_in_cb = func

    def register_for_port_stats_in(self, func):
        self.port_stats_in_cb = func

    def register_for_datapath_leave(self, func):
        self.datapath_leave_cb = func

    def register_for_datapath_join(self, func):
        self.datapath_join_cb = func

    def register_for_flow_removed(self, func):
        self.flow_removed_cb = func

    def post_callback(self, timeout, func):
        if (self.ctxt != None):
            self.ctxt.post_callback(timeout, func)

    def send_openflow(self, dp_id, buffer_id, packet, actions, inport=openflow.OFPP_CONTROLLER):
        if isinstance(actions, int) or isinstance(actions, long): # NOX API shortcut, does not follow OpenFlow specs, we translate
            actions = [[openflow.OFPAT_OUTPUT, [0, actions]]]
        if not isinstance(actions, list):
            utils.crash("Unknown action type")

        if (self.ctxt != None):
            self.ctxt.send_openflow(dp_id, buffer_id, packet, actions, inport)

    def send_flow_command(self, dp_id, command, attrs, 
                          priority=openflow.OFP_DEFAULT_PRIORITY,
                          add_args=None,
                          hard_timeout=openflow.OFP_FLOW_PERMANENT):
        if (self.ctxt != None):
            self.ctxt.send_flow_command(dp_id, command, attrs, priority, add_args, hard_timeout)

    def install_datapath_flow(self, dp_id, attrs, idle_timeout, hard_timeout, actions, buffer_id=None, priority=openflow.OFP_DEFAULT_PRIORITY, inport=None, packet=None):
        if (self.ctxt != None):
            self.ctxt.install_datapath_flow(dp_id, attrs, idle_timeout, hard_timeout, actions, buffer_id, priority, inport, packet)

    def delete_strict_datapath_flow(self, dp_id, attrs, priority=openflow.OFP_DEFAULT_PRIORITY):
        if (self.ctxt != None):
            self.ctxt.delete_strict_datapath_flow(dp_id, attrs, priority)

    @abc.abstractmethod
    def dump_equivalent_state(self):
        return { "ctxt": utils.copy_state(self.ctxt) }

    def __deepcopy__(self, memo):
        cctxt = copy.deepcopy(self.ctxt, memo)
        c = type(self)(cctxt)
        memo[id(self)] = c
        d = c.__dict__
        for k in self.__dict__:
            if k == "packet_in_cb":
                d[k] = self.packet_in_cb
                continue
            elif k == "datapath_leave_cb":
                d[k] = self.datapath_leave_cb
                continue
            elif k == "datapath_join_cb":
                d[k] = self.datapath_join_cb
                continue
            elif k == "flow_removed_cb":
                d[k] = self.flow_removed_cb
                continue
            elif k == "port_status_cb":
                d[k] = self.port_status_cb
                continue
            elif k == "ctxt":
                continue
            try:
                d[k] = copy.deepcopy(self.__dict__[k], memo)
            except RuntimeError:
                utils.crash(k)
        if hasattr(self, "custom_copy"):
            if memo["get_app_state"]:
                self.custom_copy(c, memo)
        else:
            utils.crash("custom copy not implemented in Component subclass")
        return c

