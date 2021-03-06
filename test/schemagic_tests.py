from collections import defaultdict
from pprint import pprint
from unittest.case import TestCase

import itertools

from schemagic.core import validate_against_schema
from schemagic.utils import separate_dict
from schemagic.validators import formatted_string, null, or_, enum

test_cases = {
    validate_against_schema: {
        "showing an error when given int instead of list of ints":
            dict(schema=[int],
                 value=5,
                 result=TypeError),
        "returning unmodified list of ints when validating [int] template sequence":
            dict(schema=[int],
                 value=[5, 6],
                 result=[5, 6]),
        "validating with str function with correct data":
            dict(schema=str,
                 value="hello",
                 result="hello"),
        "validating with int function with incorrect data":
            dict(schema=int,
                 value="hello",
                 result=ValueError),
        "validating map template with correct data":
            dict(schema={int: str},
                 value= {1: "hello", 2: "world"},
                 result= {1: "hello", 2: "world"}),
        "validating strict sequence with good data":
            dict(schema=[int, int],
                 value=[1, 2],
                 result=[1, 2]),
        "validating strict sequence with bad data":
            dict(schema=[int, int],
                 value=[1],
                 result=ValueError),
    },
    formatted_string(r"\d+"):{
        "throwing error when incorrectly formatted string passed as data":
            dict(data="not a digit",
                 result=ValueError
            ),
        "returning string when properly formatted":
            dict(data="112233",
                 result="112233"),
        "stringifing data before checking - and returning as string":
            dict(data=112233,
                 result="112233")
    },
    null:{
        "throws error when recieves string":
            dict(data="hello",
                 result=ValueError)
    },
    or_(int, float):{
        "allowing ints":
            dict(data=10,
                 result=10),
        "allowing floats":
            dict(data=10.5,
                 result=10.5),
        "throwing error when passed string":
            dict(data="hello",
                 result=ValueError)
    },
    enum("Hello", 5):{
        "allowing string \"Hello\"": dict(data="Hello", result="Hello"),
        "allowing int 5": dict(data=5, result=5),
        "rejecting int 6": dict(data=6, result=ValueError),
        "rejecting string \"World\"": dict(data="World", result=ValueError)
    }
}

def capture_errors(fn_with_possible_errors):
    try:
        return fn_with_possible_errors()
    except Exception as e:
        return e.__class__


def run_tests(test_cases):
    test_results = defaultdict(list)
    for test_fn, test_definitions in test_cases.items():
        for test_motivation, test_definition in test_definitions.items():
            split_out_test_parameters = separate_dict(test_definition, "result", "test_motivation")
            test_kwargs, expected_result = split_out_test_parameters[0], split_out_test_parameters[1]["result"]
            test_result = capture_errors(lambda: test_fn(**test_kwargs))
            test_results[test_fn.__name__].append(test_result == expected_result or "Not {0} as expected. expected: {1} got: {2}".format(test_motivation, expected_result, test_result))
    return test_results

class SchemagicTests(TestCase):
    def test_all_test_cases_passing(self):
        self.assertTrue(all(itertools.chain.from_iterable(run_tests(test_cases).values())))
