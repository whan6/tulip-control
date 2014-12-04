# Copyright (c) 2014 by California Institute of Technology
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the California Institute of Technology nor
#    the names of its contributors may be used to endorse or promote
#    products derived from this software without specific prior
#    written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL CALTECH
# OR THE CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
"""Code generation and exporting of controllers from TuLiP

Routines in this module are cross-cutting in the sense that they
concern multiple aspects of solutions created by TuLiP and accordingly
should not be placed under a specific subpackage, like tulip.transys.
"""

import time


def write_python_case(filename, *args, **kwargs):
    with open(filename, "w") as f:
        f.write(python_case(*args, **kwargs))

def python_case(M, classname="TulipStrategy"):
    """Export MealyMachine as Python class based on flat if-else block

    Assumptions
    ===========
    - Initial state is "Sinit".

    @type M: L{MealyMachine}
    @rtype: str
    """
    tab = 4*" "
    nl = "\n"
    state_table = dict([(s,i) for (i,s) in enumerate(M.states)])
    if len(M.outputs) == 1:
        output_prefix = ""
        output_suffix = ""
    else:
        output_prefix = "("
        output_suffix = ")"
    output_tuple = output_prefix+", ".join([str(v) for v in M.outputs])+output_suffix

    code = "class "+classname+":" + nl

    code += tab + "\"\"\"" + 2*nl
    code += tab + "Automatically generated by tulip.dumpsmach on "+time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()) + nl
    code += tab + "To learn more about TuLiP, visit http://tulip-control.org" + nl
    code += tab + "\"\"\"" + nl

    code += tab + "def __init__(self):"+nl
    code += 2*tab+"self.state = "+str(state_table["Sinit"]) + 2*nl

    code += tab + "def move(self"
    if len(M.inputs) > 0:
        code += ", "+", ".join(M.inputs)
    code += "):" + nl
    code += 2*tab + "\"\"\"Given inputs, take move and return outputs." + 2*nl
    code += 2*tab + "@return: "+output_tuple + nl
    code += 2*tab + "\"\"\"" + nl
    first = True
    for state in M.states:
        code += 2*tab
        if first:
            first = False
            code += "if"
        else:
            code += "elif"
        code += " self.state == "+str(state_table[state])+":" + nl

        first = True
        for (from_state, to_state, label_dict) in M.transitions(nbunch=(state,),
                                                                data=True):
            assert from_state == state
            code += 3*tab
            if first:
                first = False
                code += "if"
            else:
                code += "elif"
            if len(M.inputs) > 0:
                code += " (" + ") and (".join([str(k)+" == "+str(v) for (k,v) in label_dict.items() if k in M.inputs])+"):" + nl
            else:
                code += " True:" + nl
            code += 4*tab + "self.state = "+str(state_table[to_state]) + nl
            code += 4*tab + (nl+4*tab).join([str(k)+" = "+str(v) for (k,v) in label_dict.items() if k in M.outputs]) + nl

        if len(M.inputs) > 0:
            code += 3*tab + "else:" + nl
            code += 4*tab + "raise Exception(\"Unrecognized input: "
            code += "+\";".join([" "+str(v)+" = \"+str("+str(v)+")" for v in M.inputs])
            code += ")" + nl

    code += 2*tab + "else:" + nl
    code += 3*tab + "raise Exception(\"Unrecognized internal state: \"+str(self.state))" + nl

    code += 2*tab + "return " + output_tuple + nl

    return code
