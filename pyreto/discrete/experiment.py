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

""" Defines an experiment that matches up agents with tasks and handles their
    interaction.
"""

import time
import logging

logger = logging.getLogger(__name__)


class MarketExperiment(object):
    """ Defines an experiment that matches up agents with tasks and handles
        their interaction.
    """

    def __init__(self, tasks, agents, market):
        """ Initialises the market experiment.
        """
#        super(MarketExperiment, self).__init__(None, None)

        assert len(tasks) == len(agents)

        #: Tasks associate and agent with its environment.
        self.tasks = tasks

        #: Agents capable of producing actions based on previous observations.
        self.agents = agents

        #: Market to which agents submit offers/bids.
        self.market = market

        #----------------------------------------------------------------------
        #  "Experiment" interface:
        #----------------------------------------------------------------------

        self.stepid = 0

    #--------------------------------------------------------------------------
    #  "Experiment" interface:
    #--------------------------------------------------------------------------

    def doInteractions(self, number=1):
        """ Directly maps the agents and the tasks.
        """
        t0 = time.time()

        for _ in range(number):
            self._oneInteraction()

        elapsed = time.time() - t0
        logger.info("%d interactions executed in %.3fs." % (number, elapsed))

        return self.stepid


    def _oneInteraction(self):
        """ Coordinates one interaction between each agent and its environment.
        """
        self.stepid += 1

        logger.info("\nEntering simulation period %d." % self.stepid)

        # Initialise the market.
        self.market.reset()

        # Get an action from each agent and perform it.
        for task, agent in zip(self.tasks, self.agents):
            observation = task.getObservation()
            agent.integrateObservation(observation)

            action = agent.getAction()
            task.performAction(action)

        # Clear the market.
        self.market.run()

        # Reward each agent appropriately.
        for task, agent in zip(self.tasks, self.agents):
            reward = task.getReward()
            agent.giveReward(reward)

        # Instruct each agent to learn from it's actions.
#        for agent in self.agents:
#            agent.learn()

#        logger.info("")


    def reset(self):
        """ Sets initial conditions for the experiment.
        """
        self.stepid = 0

        for task, agent in zip(self.tasks, self.agents):
            task.env.reset()

            agent.module.reset()
            agent.history.reset()
#            agent.history.clear()
