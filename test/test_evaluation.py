# -*- coding: utf-8 -*-
from .helper import session, check_evaluation

import sys
import pytest

@pytest.mark.parametrize(
    "str_expr,str_expected",
    [
        # Table tests
        (r"Table[F[x],{x,1,3}]", "{F[1],F[2],F[3]}"),
        (r"Table[F[x],{x,{1,2,3}}]", "{F[1],F[2],F[3]}"),
        (r"s={1,2,3};Table[F[x],{x,s}]", "{F[1],F[2],F[3]}"),
        (r"s={x,1,3};Table[F[x],s]", "{F[1],F[2],F[3]}"),
        (r"s={x,{1,2,3}};Table[F[x],s]", "{F[1],F[2],F[3]}"),
        (r"s={x,{1,2,3}};Table[F[x],s]", "{F[1],F[2],F[3]}"),
        # Global System Information
        (r"Abs[$ByteOrdering]", "1"),
        (r"Head[$CommandLine]", "List"),
        (r"Head[$Machine]", "String"),
        (r"Head[$MachineName]", "String"),
        (r"""Length[Names["System`*"]] > 1024""", "True"),
        (r"Length[$Packages] >= 5", "True"),
        (r"Head[$ParentProcessID]", "Integer"),
        (r"Head[$ProcessID]", "Integer"),
        (r"Head[$ProcessorType]", "String"),
        (r"Head[$ScriptCommandLine]", "List"),
        (r"Head[$SystemID]", "String"),
        (r"Head[$SystemWordLength]", "Integer"),
        # This doesn't work if not logged or in some OS's
        # (r"Head[$UserName]", "String"),
        (r"Head[$Version]", "String"),
        # Strings and Characters
        (r'StringInsert["abcdefghijklm", "X", 1]', r'"Xabcdefghijklm"'),
        (r'StringInsert["abcdefghijklm", "X", 14]', r'"abcdefghijklmX"'),
        (r'StringInsert["abcdefghijklm", "", 1]', r'"abcdefghijklm"'),
        (r'StringInsert["", "X", 1]', r'"X"'),
        (r'StringInsert["", "X", -1]', r'"X"'),
        (r'StringInsert["abcdefghijklm", "", -1]', r'"abcdefghijklm"'),
        (
            r'StringInsert[{"abcdefghijklm", "Mathics"}, "X", {}]',
            r'{"abcdefghijklm", "Mathics"}',
        ),
    ],
)
def test_evaluation(str_expr: str, str_expected: str, message=""):
    result = session.evaluate(str_expr)
    expected = session.evaluate(str_expected)

    if message:
        assert result == expected, message
    else:
        assert result == expected


def test_optionvalues():
    session.evaluate("ClearAll[q];ClearAll[a];ClearAll[s]; Options[f1]:={q->12}")
    session.evaluate("f1[x_,OptionsPattern[]]:=x^OptionValue[q]")
    result =  session.evaluate('f1[y]')
    expected = session.evaluate('y ^ 12')
    assert(result == expected)

    # FIXME: Still needs fixing.
    # session.evaluate("Options[f2]:={s->12}")
    # session.evaluate("f2[x_,opt:OptionsPattern[]]:=x^OptionValue[s]")
    # result =  session.evaluate('f2[y]')
    # expected = session.evaluate('y ^ 12')
    # assert(result == expected)

    session.evaluate("Options[f3]:={a->12}")
    session.evaluate("f3[x_,opt:OptionsPattern[{a:>4}]]:=x^OptionValue[a]")
    result =  session.evaluate('f3[y]')
    expected = session.evaluate('y ^ 4')
    assert(result == expected)

    session.evaluate("Options[f4]:={a->12}")
    session.evaluate("f4[x_,OptionsPattern[{a:>4}]]:=x^OptionValue[a]")
    result =  session.evaluate('f4[y]')
    expected = session.evaluate('y ^ 4')
    assert(result == expected)


    session.evaluate("Options[F]:={a->89,b->37}")
    result = session.evaluate("OptionValue[F, a]")
    expected = session.evaluate('89')
    assert(result == expected)

    result = session.evaluate("OptionValue[F, {a,b}]")
    expected = session.evaluate('{89, 37}')
    assert(result == expected)

    result = session.evaluate("OptionValue[F, {a,b, l}]")
    expected = session.evaluate('{89, 37, OptionValue[l]}')
    msg = "OptionValue::optnf: Option name l not found."
    assert result == expected, msg

    result = session.evaluate("OptionValue[F, {l->77}, {a,b, l}]")
    expected = session.evaluate('{89, 37, 77}')
    assert(result == expected)

    result = session.evaluate("OptionValue[F, {b->-1, l->77}, {a,b, l}]")
    expected = session.evaluate('{89, -1, 77}')
    assert(result == expected)

if sys.platform in ("linux",):

    def test_system_specific_long_integer():
        session.evaluate("""
        WRb[bytes_, form_] := Module[{str, res={}, byte}, str = OpenWrite[BinaryFormat -> True];
        BinaryWrite[str, bytes, form];
        str = OpenRead[Close[str], BinaryFormat -> True];
        While[Not[SameQ[byte = BinaryRead[str], EndOfFile]], res = Join[res, {byte}];];
        Close[str]; res]
        """)
        for str_expr, str_expected, message in (
            (
                r'WRb[{1885507541, 4157323149}, Table["UnsignedInteger32", {2}]]',
                r"{213, 143, 98, 112, 141, 183, 203, 247}",
                "UnsignedInteger32",
            ),
            (
                r'WRb[{384206740, 1676316040}, Table["UnsignedInteger32", {2}]]',
                r"{148, 135, 230, 22, 136, 141, 234, 99}",
                "UnsignedInteger32 - 2nd test",
            ),
            (
                r'WRb[7079445437368829279, "UnsignedInteger64"]',
                r"{95, 5, 33, 229, 29, 62, 63, 98}",
                "UnsignedInteger64",
            ),
            (
                r'WRb[5381171935514265990, "UnsignedInteger64"]',
                r"{134, 9, 161, 91, 93, 195, 173, 74}",
                "UnsignedInteger64 - 2nd test",
            ),
            (
                r'WRb[293382001665435747348222619884289871468, "UnsignedInteger128"]',
                r"{108, 78, 217, 150, 88, 126, 152, 101, 231, 134, 176, 140, 118, 81, 183, 220}",
                "UnsignedInteger128",
            ),
            (
                r'WRb[253033302833692126095975097811212718901, "UnsignedInteger128"]',
                r"{53, 83, 116, 79, 81, 100, 60, 126, 202, 52, 241, 48, 5, 113, 92, 190}",
                "UnsignedInteger128 - 2nd test",
            ),
        ):

            check_evaluation(str_expr, str_expected, message)

# import os.path as osp
# def check_evaluation_with_err(str_expr: str, expected: str, message=""):
#     import pdb; pdb.set_trace()
#     result = session.evaluate(str_expr)

#     if message:
#         assert result == expected, message
#     else:
#         assert result == expected

# if osp.exists("/dev/zero"):
#     def test_system_specific_write_string():
#         for str_expr, str_expected, message in (
#             (
#                 r'WriteString[OpenWrite["/dev/full"], "123"]',
#                 r": No space left on device.",
#                 "WriteString to full device",
#             ),
#             # (
#             #     r'Close[str]',
#             #     r"No space left on device.",
#             #     "Close on full device",
#             # ),
#         ):

#             check_evaluation_with_err(str_expr, str_expected, message)


def test_exit():
    global session
    try:
        session.evaluate("Exit[-37]")
    except SystemExit as e:
        assert e.code == -37


def test_quit():
    try:
        session.evaluate("Quit[-37]")
    except SystemExit as e:
        assert e.code == -37
