import json
import logging
import random
import time

import click
import confluent_kafka

from cli.mutex import Mutex
from generator.generator import make_generator


def generate(generator, count, produce, interval):
    try:
        for i in range(count):
            msg = generator()
            produce(json.dumps(msg))
            time.sleep(interval / 1000)
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
@click.option(
    "--schema",
    cls=Mutex,
    not_required_if=["path"],
    help="JSON schema.",
)
@click.option("--count", default=1, help="Number of JSON objects to produce.")
@click.option("--seed", default=None, help="Seed for PRNG.")
@click.option(
    "--arr-len",
    "arr_len_range",
    type=(int, int),
    default=(0, 32),
    show_default=True,
    help="Min and max number of elements for arrays.",
)
@click.option(
    "--int",
    "int_range",
    type=(int, int),
    default=(0, 1 << 16),
    show_default=True,
    help="Min and max values for integers.",
)
@click.option(
    "--float",
    "float_range",
    type=(float, float),
    default=(0, 1 << 16),
    show_default=True,
    help="Min and max values for floating points.",
)
@click.option(
    "--str-len",
    "str_len_range",
    type=(int, int),
    default=(2, 16),
    show_default=True,
    help="Min and max length for strings.",
)
@click.option(
    "--interval",
    default=0,
    show_default=True,
    help="The interval (in ms) between each JSON.",
)
@click.option("--kafka", type=(str, str), help="Kafka server and topic.")
def main(
    path,
    schema,
    count,
    seed,
    arr_len_range,
    int_range,
    float_range,
    str_len_range,
    interval,
    kafka,
):
    if not path and not schema:
        click.echo(click.get_current_context().get_help())
        return
    if path:
        with open(path) as f:
            top_lvl_schema = json.loads(f.read())
    if schema:
        top_lvl_schema = json.loads(schema)

    random.seed(seed)

    arr_min_items, arr_max_items = arr_len_range
    num_min_val, num_max_val = int_range
    float_min_val, float_max_val = float_range
    str_min_len, str_max_len = str_len_range

    generator = make_generator(
        top_lvl_schema,
        arr_min_items,
        arr_max_items,
        num_min_val,
        num_max_val,
        float_min_val,
        float_max_val,
        str_min_len,
        str_max_len,
    )

    if kafka:
        server, topic = kafka
        kafka_producer = confluent_kafka.Producer({"bootstrap.servers": server})
        produce = lambda json: kafka_producer.produce(topic, json)
        generate(generator, count, produce, interval)
        kafka_producer.flush()
    else:
        produce = lambda json: print(json)
        generate(generator, count, produce, interval)


if __name__ == "__main__":
    main()
