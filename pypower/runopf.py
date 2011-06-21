# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

from sys import stdout, stderr

from ppoption import ppoption
from opf import opf
from printpf import printpf
from savecase import savecase


def runopf(casedata='case9', ppopt=None, fname='', solvedcase=''):
    """ Runs an optimal power flow.

    @see: L{rundcopf}, L{runuopf}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ## default arguments
    ppopt = ppoption(ppopt)

    ##-----  run the optimal power flow  -----
    r = opf(casedata, ppopt)

    ##-----  output results  -----
    if fname:
        fd = None
        try:
            fd = open(fname, "wb")
        except IOError, detail:
            stderr.write("Error opening %s: %s.\n" % (fname, detail))
        finally:
            if fd is not None:
                printpf(r, fd, ppopt)
                fd.close()

    printpf(r, stdout, ppopt)

    ## save solved case
    if solvedcase:
        savecase(solvedcase, r)

    return r
