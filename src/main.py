from collections import OrderedDict
import json
import sys
from generator import make_generator, load_definitions
import pprint


def main():
    with open(sys.argv[1]) as f:
        top_lvl_schema = json.loads(f.read())
        definitions = load_definitions(top_lvl_schema)
        generator = make_generator(schema=top_lvl_schema, definitions=definitions)
        for _ in range(1):
            msg = generator()
            print(json.dumps(msg))


if __name__ == "__main__":
    main()
