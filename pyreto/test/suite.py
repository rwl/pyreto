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

""" Pyreto test suite.
"""

import unittest

from pylon.test.suite import suite as pylon_suite

from market_test import DCMarketTestCase
from experiment_test import MarketExperimentTest


def suite():
    """ Returns the Pyreto test suite.
    """
    # Pyreto tests are in addition to the Pylon tests.
    suite = pylon_suite()

    suite.addTest(unittest.makeSuite(DCMarketTestCase))
    suite.addTest(unittest.makeSuite(MarketExperimentTest))

    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
