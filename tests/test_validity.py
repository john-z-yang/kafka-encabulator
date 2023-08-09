import json
import os
import random

import jsonschema
import pytest

from src.generator.generator import make_generator

SCHEMA_FILES = [
    "events.v1.schema.json",
    "profile-functions.v1.schema.json",
    "generic-events.v1.schema.json",
    "profile-metadata.v1.schema.json",
    "group-attributes.v1.schema.json",
    "snuba-generic-metrics.v1.schema.json",
    "ingest-metrics.v1.schema.json",
    "snuba-metrics.v1.schema.json",
    "ingest-replay-events.v1.schema.json",
    "snuba-queries.v1.schema.json",
    "ingest-replay-recordings.v1.schema.json",
    "subscription-results.v1.schema.json",
    "outcomes.v1.schema.json",
    "transactions.v1.schema.json",
]

SCHEMA_PATHS = [
    f"{os.path.dirname(__file__)}/../lib/schemas/{schema_file}"
    for schema_file in SCHEMA_FILES
]


@pytest.mark.parametrize(
    "schema_path",
    SCHEMA_PATHS,
)
def test_generated_schema_is_valid(schema_path):
    random.seed(0)
    with open(schema_path) as f:
        schema = json.loads(f.read())
        generator = make_generator(top_lvl_schema=schema)
        for _ in range(256):
            msg = generator()
            jsonschema.validate(instance=msg, schema=schema)
