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

from hy.models.expression import HyExpression
from hy.models.string import HyString
from hy.models.symbol import HySymbol
from hy.models.list import HyList

from collections import defaultdict

_hy_macros = defaultdict(dict)
_hy_macro_handlers = {}


def macro(name):
    def _(fn):
        module_name = fn.__module__
        if module_name.startswith("hy.core"):
            module_name = None
        _hy_macros[module_name][name] = fn
        return fn
    return _


def require(source_module_name, target_module_name):
    macros = _hy_macros[source_module_name]
    refs = _hy_macros[target_module_name]
    for name, macro in macros.items():
        refs[name] = macro


def set_macro_handler(symbol, handler):
    _hy_macro_handlers[symbol] = handler


def default_handler(tree, module_name):
    return HyExpression([tree[0]] +
                        [process(x, module_name) for x in tree[1:]])


def no_macro_expansion(tree, module_name):
    return tree


def try_expr(tree, module_name):

    def clause_handler(tree, module_name):
        if isinstance(tree, HyExpression) and len(tree) > 1:
            return default_handler(tree, module_name)
        else:
            return tree

    if len(tree) == 1:
        # Emtpy (try)
        return tree
    body = process(tree[1], module_name)
    clauses = [clause_handler(x, module_name) for x in tree[2:]]
    return HyExpression([tree[0], body] + clauses)


def with_expr(tree, module_name):
    # (with [fd (open "README.md" "r")] (assert fd))
    # (with [(open "README.md" "r")] (do)))
    pass


def list_comp_expr(tree, module_name):
    # (assert (= (list-comp (* x 2) (x (range 2))) [0 2]))
    # (assert (= (list-comp (* x 2) (x (range 4)) (% x 2)) [2 6]))
    # (assert (= (sorted (list-comp (* y 2) ((, x y) (.items {"1" 1 "2" 2}))))
    #            [2 4]))
    # (assert (= (list-comp (, x y) (x (range 2) y (range 2)))
    #            [(, 0 0) (, 0 1) (, 1 0) (, 1 1)]))
    # (assert (= (list-comp j (j [1 2])) [1 2])))
    pass


def process(tree, module_name):
    if isinstance(tree, HyExpression):
        fn = tree[0]
        if isinstance(fn, HyString):
            handler = _hy_macro_handlers.get(fn, default_handler)
            ntree = handler(tree, module_name)
        else:
            ntree = default_handler(tree, module_name)
        if ntree is not tree:
            ntree.replace(tree)

        if isinstance(fn, HyString):
            m = _hy_macros[module_name].get(fn)
            if m is None:
                m = _hy_macros[None].get(fn)
            if m is not None:
                obj = m(*ntree[1:])
                obj.replace(tree)
                return obj

        ntree.replace(tree)
        return ntree

    if isinstance(tree, HyList):
        obj = tree.__class__([process(x, module_name) for x in tree])  # NOQA
        # flake8 thinks we're redefining from 52.
        obj.replace(tree)
        return obj

    if isinstance(tree, list):
        return [process(x, module_name) for x in tree]

    return tree
