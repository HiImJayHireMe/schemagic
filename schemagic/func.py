from functools import partial, wraps

from schemagic.core import validate_against_schema
from schemagic.validators import date_string

ALWAYS = lambda: True
WHEN_DEBUGGING = lambda: __debug__
IDENTITY = lambda x: x

def validator(schema, message, coerce_data=True, data=None):
    if data is None:
        return partial(validator, schema, message, coerce_data)
    try:
        coerced_and_validated_data = validate_against_schema(schema, data)
        return coerced_and_validated_data if coerce_data else data
    except Exception as e:
        message_details = {
            "subject": message,
            "error": "{0}: {1}".format(e.__class__.__name__, e),
            "value": data,
            "schema": schema
        }
        raise ValueError("Bad value provided for {subject}. - error: {error} schema: {schema} value: {value}".format(**message_details))

def validated(validation_predicate=None, coerce_data=True, input_schema=None, output_schema=None, fn=None):
    if fn is None:
        return partial(validated, validation_predicate, coerce_data, input_schema, output_schema)

    validation_predicate = validation_predicate or WHEN_DEBUGGING
    input_validator = validator(input_schema or IDENTITY, "input to function {0}".format(fn.__name__), coerce_data)
    output_validator = validator(output_schema or IDENTITY, "output from function {0}".format(fn.__name__), coerce_data)

    @wraps(fn)
    def _fn(*args, **kwargs):
        if validation_predicate():
            validated_args, validated_kwargs = validate_function_input(input_validator, args, kwargs)
            return output_validator(fn(*validated_args, **validated_kwargs))
        else:
            return fn(*args, **kwargs)
    return _fn

def validate_function_input(input_validator, arg_list, kwarg_dict):
    if arg_list and kwarg_dict:
        validated_input = input_validator(arg_list + tuple([kwarg_dict]))
        args, kwargs = validated_input[:-1], validated_input[-1]
    elif kwarg_dict:
        validated_input = input_validator(kwarg_dict)
        args, kwargs = [], validated_input
    elif arg_list and len(arg_list) > 1:
        validated_input = input_validator(arg_list)
        args, kwargs = validated_input, {}
    elif arg_list and len(arg_list) is 1:
        validated_input = input_validator(arg_list[0])
        args, kwargs = [validated_input], {}
    else:
        args, kwargs = arg_list, kwarg_dict
    return args, kwargs

if __name__ == '__main__':
    import operator

    my_validator = partial(validated, ALWAYS)

    @my_validator(input_schema=[int], output_schema=[date_string])
    def sum_things(*numbers):
        return reduce(operator.add, numbers)

    print sum_things(1,2,3)