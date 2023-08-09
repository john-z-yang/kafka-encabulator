# kafka-encabulator

Python script that generates random JSONs base on JSON schema.

## Example

`schema.json`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "generic_event",
  "anyOf": [
    { "$ref": "#/definitions/foo" },
    { "$ref": "#/definitions/bar" }
  ],
  "definitions": {
    "foo": {
      "type": "array",
      "items": [
        { "const": 2 },
        {
          "type": "object",
          "properties": {
            "id": {
              "type": "string",
              "pattern": "[0-9a-fA-F]{32}"
            },
            "xyz": {
              "type": [ "integer", "null" ],
              "minimum": 0,
              "maximum": 8
            }
          }
        },
        { "$ref": "#/definitions/bar" }
      ]
    },
    "bar": {
      "type": [ "boolean", "null" ]
    }
  }
}
```

```bash
➜  kafka-encabulator git:(cli) ✗ python src/main.py --path schema.json --count 8
null
[2, {"id": "aEBDba6BbBa9800f68ed02fa0cfCecc6", "xyz": 8}, true]
false
[2, {"id": "4769bf9a7CC4f7a4cEa7CdD0bcFEBa98", "xyz": null}, null]
[2, {"id": "ad07c6FD3aEfeF72cE6eDbda101aFcE7", "xyz": null}, null]
[2, {"id": "668c14f2bAC85df30834BcFDAC8476Df", "xyz": 0}, null]
[2, {"id": "aDAD79dbAeB0B20ab6241BFb99f8eBAd", "xyz": null}, false]
null
```

## Getting Started

Usage

```
Usage: main.py [OPTIONS]

Options:
  --path PATH             The file path of the JSON schema (mutually exclusive
                          with --schema).
  --schema TEXT           The JSON schema. (mutually exclusive with --path).
  --count INTEGER         Number of JSON objects to produce.
  --kafka <TEXT TEXT>...  The kafka server and topic.
  --help                  Show this message and exit.
```

Top-level Makefile synopsis

```
    make         - setup requirements
    make steup   - same as above
    make test    - run all unit tests
    make clean   - removes cache files
```

