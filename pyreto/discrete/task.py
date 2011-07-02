# Copyright (C) 2007-2010 Richard Lincoln
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY], without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

""" Defines a profit maximisation task.
"""

import logging

from scipy import power

from pybrain.rl.environments import Task

logger = logging.getLogger(__name__)


class ProfitTask(Task):
    """ Defines a task with discrete observations of the clearing price.
    """

    def __init__(self, environment, maxSteps=24, discount=None):
        super(ProfitTask, self).__init__(environment)

        #: Maximum number of time steps.
        self.maxSteps = maxSteps

        #: Current time step.
        self.t = 0

        #: Record of generator status for startup/shutdown costs.
        self._gOnline = [g.online for g in environment.generators]

        #----------------------------------------------------------------------
        #  "EpisodicTask" interface:
        #----------------------------------------------------------------------

        #: Discount factor.
        self.discount = discount

        #: Track cumulative reward.
        self.cumulativeReward = 0

        #: Track the number of samples.
        self.samples = 0

    #--------------------------------------------------------------------------
    #  "Task" interface:
    #--------------------------------------------------------------------------

    def getReward(self):
        """ Returns the reward corresponding to the last action performed.
        """
        t = self.env.market.period

        # Compute revenue minus costs.
        totalEarnings = 0.0
        for g in self.env.generators:
            # Compute costs in $ (not $/hr).
            costs = g.total_cost(round(g.p, 4),
                                 self.env._g0[g]["p_cost"],
                                 self.env._g0[g]["pcost_model"])

            offbids = [ob for ob in self.env._lastAction if ob.generator == g]

            revenue = t * sum([ob.revenue for ob in offbids])
            if offbids:
                revenue += offbids[0].noLoadCost

            if g.is_load:
                earnings = costs - revenue
            else:
                earnings = revenue - costs#(fixedCost + variableCost)

            logger.debug("Generator [%s] earnings: %.2f (%.2f, %.2f)" %
                         (g.name, earnings, revenue, costs))

            totalEarnings += earnings

        # Startup/shutdown costs.
        onlineCosts = 0.0
        for i, g in enumerate(self.env.generators):
            if self._gOnline[i] and not g.online:
                onlineCosts += g.c_shutdown
            elif not self._gOnline[i] and g.online:
                onlineCosts += g.c_startup
        self._gOnline = [g.online for g in self.env.generators]

        reward = totalEarnings - onlineCosts
        self.addReward(reward)

        logger.debug("Task reward: %.2f (%.2f - %.2f)" %
                     (reward, totalEarnings, onlineCosts))

        return reward


    def performAction(self, action):
        """ The action vector is stripped and the only element is cast to
            integer and given to the super class.
        """
        self.t += 1
        super(ProfitTask, self).performAction(int(action[0]))
        self.samples += 1


#    def getReward(self):
#        """ Returns the reward corresponding to the last action performed.
#        """
#        earnings = super(ProfitTask, self).getReward()
#        self.addReward(earnings)
#        return earnings


    def reset(self):
#        super(ProfitTask, self).reset()
#        self.env.reset()
        self.cumulativeReward = 0
        self.samples = 0
        self.t = 0

    #--------------------------------------------------------------------------
    #  "EpisodicTask" interface:
    #--------------------------------------------------------------------------

    def isFinished(self):
        """ Is the current episode over?
        """
        if self.t >= self.maxSteps:
            return True # maximal timesteps
        return False


    def addReward(self, r=None):
        """ A filtered mapping towards performAction of the underlying
            environment.
        """
        r = self.getReward() if r is None else r

        # by default, the cumulative reward is just the sum over the episode
        if self.discount:
            self.cumulativeReward += power(self.discount, self.samples) * r
        else:
            self.cumulativeReward += r
