# Copyright (C) 2009 Power System Engineering Research Center
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
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

from numpy import ndim

def get_reorder(A, idx, dim=1):
    """Returns A with one of its dimensions indexed.

    B = get_reorder(A, idx, dim)

    Returns A(:, ..., :, idx, :, ..., :), where dim determines
    in which dimension to place the idx.

    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ndims = ndim(A)
    if ndims == 1:
        B = A[idx]
    elif ndims == 2:
        if dim == 1:
            B = A[idx, :]
        elif dim == 2:
            B = A[: idx]
        else:
            raise ValueError
    else:
        raise ValueError

    return B