# Copyright (C) 1996-2010 Power System Engineering Research Center
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from time import time

from numpy import copy
from numpy import flatnonzero as find

from pypower.opf_args import opf_args
from pypower.ppoption import ppoption
from pypower.isload import isload
from pypower.totcost import totcost
from pypower.fairmax import fairmax
from pypower.opf import opf

from pypower.idx_bus import *
from pypower.idx_gen import *

def uopf(*args, **kw_args):
    """ Solves combined unit decommitment / optimal power flow.

    Solves a combined unit decommitment and optimal power flow for a single
    time period. Uses an algorithm similar to dynamic programming. It proceeds
    through a sequence of stages, where stage N has N generators shut down,
    starting with N=0. In each stage, it forms a list of candidates (gens at
    their Pmin limits) and computes the cost with each one of them shut down.
    It selects the least cost case as the starting point for the next stage,
    continuing until there are no more candidates to be shut down or no
    more improvement can be gained by shutting something down.
    If VERBOSE in ppopt (see PPOPTION) is true, it prints progress
    info, if it is > 1 it prints the output of each individual opf.

    @see: L{opf}, L{runuopf}
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ##----- initialization -----
    t0 = time()                                 ## start timer

    ## process input arguments
    ppc, ppopt = opf_args(args, kw_args)

    ## options
    verbose = ppopt["VERBOSE"]
    if verbose:      ## turn down verbosity one level for calls to opf
        ppopt = ppoption(ppopt, VERBOSE=verbose - 1)

    ##-----  do combined unit commitment/optimal power flow  -----

    ## check for sum(Pmin) > total load, decommit as necessary
    on   = find( ppc["gen"][:, GEN_STATUS] > 0 and not isload(ppc["gen"]) )   ## gens in service
    onld = find( ppc["gen"][:, GEN_STATUS] > 0 and     isload(ppc["gen"]) )   ## disp loads in serv
    load_capacity = sum(ppc["bus"][:, PD]) - sum(ppc["gen"][onld, PMIN]) ## total load capacity
    Pmin = ppc["gen"][on, PMIN]
    while sum(Pmin) > load_capacity:
        ## shut down most expensive unit
        avgPmincost = totcost(ppc["gencost"][on, :], Pmin) / Pmin
        _, i = fairmax(avgPmincost)   ## pick one with max avg cost at Pmin
        i = on[i]                     ## convert to generator index

        if verbose:
            print 'Shutting down generator %d so all Pmin limits can be satisfied.\n' % i

        ## set generation to zero
        ppc["gen"][i, [PG, QG, GEN_STATUS]] = 0

        ## update minimum gen capacity
        on  = find( ppc["gen"][:, GEN_STATUS] > 0 and not isload(ppc["gen"]) )   ## gens in service
        Pmin = ppc["gen"][on, PMIN]

    ## run initial opf
    results, success = opf(ppc, ppopt)

    ## best case so far
    results1 = copy(results)

    ## best case for this stage (ie. with n gens shut down, n=0,1,2 ...)
    results0 = copy(results1)
    ppc["bus"] = results0["bus"]     ## use these V as starting point for OPF

    while True:
        ## get candidates for shutdown
        candidates = find(results0["gen"][:, MU_PMIN] > 0 & results0["gen"][:, PMIN] > 0)
        if len(candidates) == 0:
            break

        done = True   ## do not check for further decommitment unless we
                      ##  see something better during this stage
        for k in candidates:
            ## start with best for this stage
            ppc["gen"] = results0["gen"]

            ## shut down gen k
            ppc["gen"][k, [PG, QG, GEN_STATUS]] = 0

            ## run opf
            results, success = opf(ppc, ppopt)

            ## something better?
            if success & results["f"] < results1["f"]:
                results1 = copy(results)
                k1 = k
                done = False   ## make sure we check for further decommitment

        if done:
            ## decommits at this stage did not help, so let's quit
            break
        else:
            ## shutting something else down helps, so let's keep going
            if verbose:
                print 'Shutting down generator %d.\n' % k1

            results0 = copy(results1)
            ppc["bus"] = results0["bus"]     ## use these V as starting point for OPF

    ## compute elapsed time
    et = time - t0

    ## finish preparing output
    success = results0.success
    results0.et = et

    return results0, success
