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
➜  kafka-encabulator git:(main) ✗ python src/main.py schema.json
[2, {"id": "AB6f1b6A2BECfBbaBa3d35cd73dA7952", "xyz": 3}, false]
```

## Getting Started

Top-level Makefile synopsis:
```
    make         - setup requirements
    make steup   - same as above
    make test    - run all unit tests
    make clean   - removes cache files
```

