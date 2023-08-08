import json
import sys
from generator import make_generator


def main():
    with open(sys.argv[1]) as f:
        top_lvl_schema = json.loads(f.read())
        generator = make_generator(top_lvl_schema=top_lvl_schema)
        for _ in range(1):
            msg = generator()
            print(json.dumps(msg))


if __name__ == "__main__":
    main()
