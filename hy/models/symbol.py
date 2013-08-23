# Copyright (c) 2013 Paul Tagliamonte <paultag@debian.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from hy.models.string import HyString


class HySymbol(HyString):
    """
    Hy Symbol. Basically a String.
    """

    def __init__(self, string):
        self += string

    def __getattr__(self, attr):
        if attr == "namespace":
            if attr not in self.__dict__:
                return None
            return self.__dict__[attr]
        raise AttributeError(attr)

# For some strange reason, it is not possible to add an attribute
# to a HySymbol inside __init__. That's the reason for having
# a pseudo-constructor function for making a symbol with a namespace.

def HyNamespacedSymbol(s, ns=None):
    s = HySymbol(s)
    if ns is not None:
        s.namespace = ns
    return s
