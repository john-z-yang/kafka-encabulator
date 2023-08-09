import json
import logging
import random

import click
import confluent_kafka

from cli.mutex import Mutex
from generator.generator import make_generator


def generate(generator, count, produce):
    try:
        for i in range(count):
            msg = generator()
            produce(json.dumps(msg))
    except KeyboardInterrupt:
        logging.error(f"Caught KeyboardInterrupt: {i} messages produced, stopping now")


@click.command()
@click.option(
    "--path",
    type=click.Path(exists=True),
    cls=Mutex,
    not_required_if=["schema"],
    help="File path of the JSON schema.",
)
@click.option("--schema", cls=Mutex, not_required_if=["path"], help="JSON schema.")
@click.option("--count", default=1, help="Number of JSON objects to produce.")
@click.option("--seed", default=0, show_default=True, help="Seed for the PRNG.")
@click.option("--kafka", type=(str, str), help="Kafka server and topic.")
def main(path, schema, count, seed, kafka):
    if path:
        with open(path) as f:
            top_lvl_schema = json.loads(f.read())
    if schema:
        top_lvl_schema = json.loads(schema)

    random.seed(seed)

    generator = make_generator(top_lvl_schema=top_lvl_schema)

    if kafka:
        server, topic = kafka
        kafka_producer = confluent_kafka.Producer({"bootstrap.servers": server})
        produce = lambda json: kafka_producer.produce(topic, json)
        generate(generator, count, produce)
        kafka_producer.flush()
    else:
        produce = lambda json: print(json)
        generate(generator, count, produce)


if __name__ == "__main__":
    main()
