import random
import string


def load_definitions(top_lvl_schema):
    closures = {}
    match top_lvl_schema:
        case {"definitions": definitions, **rest}:
            for name, schema in definitions.items():
                closures[f"#/definitions/{name}"] = make_generator(
                    schema=schema, definitions=closures
                )
    return closures


def make_generator(
    schema,
    arr_min_items=0,
    arr_max_items=32,
    num_min_val=0,
    num_max_val=1 << 16,
    float_min_val=0,
    float_max_val=1 << 16,
    str_len=8,
    definitions={},
):
    def compile(_schema):
        match _schema:
            case {"$ref": definition_path}:
                return lambda: definitions[definition_path]()
            case {"anyOf": [*choices], **rest}:
                closures = [compile(choice) for choice in choices]
                return lambda: random.choice(closures)()
            case {"type": "object", **rest}:
                closures = {
                    key: compile(sub_schema)
                    for key, sub_schema in rest.get("properties", {}).items()
                }
                return lambda: {key: closure() for key, closure in closures.items()}
            case {"type": "array", "items": [*sub_schemas], **rest}:
                closures = [compile(sub_schema) for sub_schema in sub_schemas]
                return lambda: [closure() for closure in closures]
            case {"type": "array", "items": sub_schema, **rest}:
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
            case {"type": "array", **rest}:
                return lambda: []
            case {"type": [*choices], **rest}:
                closures = [compile({"type": choice, **rest}) for choice in choices]
                return lambda: random.choice(closures)()
            case {"const": const, **rest}:
                return lambda: const
            case {"default": const, **rest}:
                return lambda: const
            case {"type": "number", **rest}:
                return lambda: random.uniform(
                    rest.get("minimum", float_min_val),
                    rest.get("maximum", float_max_val),
                )
            case {"type": "integer", **rest}:
                return lambda: random.randint(
                    rest.get("minimum", num_min_val), rest.get("maximum", num_max_val)
                )
            case {"type": "string", "enum": [*enums], **rest}:
                return lambda: random.choice(enums)
            case {"type": "string", **rest}:
                return lambda: "".join(
                    random.choices(string.ascii_uppercase, k=str_len)
                )
            case {"type": "boolean", **rest}:
                return lambda: random.choice((True, False))
            case {"type": "null", **rest}:
                return lambda: None
            case _:
                raise NotImplementedError(_schema)

    return compile(schema)
