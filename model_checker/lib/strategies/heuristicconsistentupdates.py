#
# Copyright (c) 2011, EPFL (Ecole Politechnique Federale de Lausanne)
# All rights reserved.
#
# Created by Marco Canini, Daniele Venzano, Dejan Kostic, Jennifer Rexford
# Contributed to this file: Peter Peresini
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

from lib.strategies.strategy import Strategy

import logging
log = logging.getLogger("nice.mc.strategy")

class HeuristicConsistentUpdates(Strategy):
    def __init__(self, model_checker):
        Strategy.__init__(self, model_checker)
        self.in_controller = False

    def getEnabledActions(self, state):
        actions = state.getAllEnabledActions()
        priority_actions = []
        for a in actions:
            if a.priority == True:
                priority_actions.append(a)
        if len(priority_actions) > 0:
            log.debug("Enabled priority actions: %s" % priority_actions)
            return [priority_actions[0]]
        else:
            return actions

    def onEnableAction(self, node, action):
        if self.in_controller:
            action.priority = True
            log.debug("Enabled priority action %s" % str(action))
        else:
            action.priority = False
        return action

    def chooseAction(self, state):
        action = state.enabled_actions.pop(0)
        return action

    def beginControllerCallback(self):
        self.in_controller = True

    def endControllerCallback(self):
        self.in_controller = False

