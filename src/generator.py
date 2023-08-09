import logging
import pprint
import random
import re
import string

import rstr


def make_generator(
    top_lvl_schema,
    arr_min_items=0,
    arr_max_items=32,
    num_min_val=0,
    num_max_val=1 << 16,
    float_min_val=0,
    float_max_val=1 << 16,
    str_len=8,
    definitions={},
):
    def load_definitions(schema):
        match schema:
            case {"definitions": schemas, **rest}:
                for name, schema in schemas.items():
                    definitions[f"#/definitions/{name}"] = compile(schema)

    def compile(schema):
        match schema:
            # Atomics:
            #     "type": ("null" | "boolean" | "integer" | "number" | "string")
            #
            # If we match any of these, our closure simply emits a single
            # primitive, and we're done.
            case {"type": "null", **rest}:
                return lambda: None
            case {"type": "boolean", **rest}:
                return lambda: random.choice((True, False))
            case {"type": "integer", **rest}:
                return lambda: random.randint(
                    rest.get("minimum", num_min_val), rest.get("maximum", num_max_val)
                )
            case {"type": "number", **rest}:
                return lambda: random.uniform(
                    rest.get("minimum", float_min_val),
                    rest.get("maximum", float_max_val),
                )
            case {"type": "string", **options}:
                match options:
                    case {"pattern": pattern, **rest}:
                        return lambda: rstr.xeger(re.compile(pattern))
                    case {"enum": [*enums], **rest}:
                        return lambda: random.choice(enums)
                    case _:
                        return lambda: "".join(
                            random.choices(string.ascii_uppercase, k=str_len)
                        )

            # Constants:
            #     "const": const
            # Trivially emit the constant.
            case {"const": const, **rest}:
                return lambda: const

            # References:
            #     "$ref": definition_path
            #
            # Trivially call the closure at the definition_path and forward
            # its result. It's imperative that we access values within
            # the definitions dict during run-time instead of compile-time,
            # because the closure corrosponding to that defintion may not
            # have been compiled yet.
            case {"$ref": definition_path}:
                return lambda: definitions[definition_path]()

            # Boolean algebraics:
            #     "anyOf": [ typename* ]
            #     "type": [ typename* ]
            #
            # Emit a single value randomly from the choices. This means we need
            # to compile all of the choices during compile time, and have the
            # closure call one randomly when it is invoked.
            case {"anyOf": [*choices], **rest}:
                closures = [compile(choice) for choice in choices]
                return lambda: random.choice(closures)()
            case {"type": [*choices], **rest}:
                closures = [compile({"type": choice, **rest}) for choice in choices]
                return lambda: random.choice(closures)()

            # Compound entities:
            #     {
            #       "type": "object",
            #       "properties": { (key: sub_schema)* }
            #       "patternProperties": { (pattern: sub_schema)* }
            #       ...
            #     } | {
            #       "type": "array",
            #       "items": ([sub_schema*] | sub_schema)
            #       ...
            #     }
            # Our closure needs to construct the correct entity when called, so
            # we compile the subschemas into closures, and generate the dic/list
            # by calling them.
            case {"type": "object", **rest}:
                prop_closures = {
                    key: compile(sub_schema)
                    for key, sub_schema in rest.get("properties", {}).items()
                }
                pattern_prop_closures = [
                    lambda: {rstr.xeger(re.compile(pattern)): closure()}
                    for pattern, closure in [
                        (pattern, compile(sub_schema))
                        for pattern, sub_schema in rest.get(
                            "patternProperties", {}
                        ).items()
                    ]
                ]
                return lambda: {
                    pattern_prop: val
                    for d in (
                        [{key: closure() for key, closure in prop_closures.items()}]
                        + [closure() for closure in pattern_prop_closures]
                    )
                    for pattern_prop, val in d.items()
                }
            case {"type": "array", **options}:
                match options:
                    case {"items": [*sub_schemas], **rest}:
                        closures = [compile(sub_schema) for sub_schema in sub_schemas]
                        return lambda: [closure() for closure in closures]
                    case {"items": sub_schema, **rest}:
                        closure = compile(sub_schema)
                        return lambda: [
                            closure()
                            for _ in range(
                                random.randint(
                                    rest.get("minItems", arr_min_items),
                                    rest.get("maxItems", arr_max_items),
                                )
                            )
                        ]
                    case _:
                        return lambda: []

            # Default value:
            #     "default": value
            #
            # We're not able to pattern match anything, so we fallback to the
            # default value if it exists. This is in the end because we want to
            # generate random values if possible.
            case {"default": value, **rest}:
                return lambda: value

            case _:
                logging.warning(
                    f"Unimplemented schema: {pprint.pformat(schema)}, emitting empty object."
                )
                return lambda: {}

    load_definitions(top_lvl_schema)
    return compile(top_lvl_schema)
