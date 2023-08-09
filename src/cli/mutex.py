import click


class Mutex(click.Option):
    def __init__(self, *args, **kwargs):
        self.not_required_if = kwargs.pop("not_required_if")

        assert self.not_required_if, "'not_required_if' parameter required"
        kwargs["help"] = (
            f"{kwargs.get('help', '')} (mutually exclusive with {', '.join([f'--{opt}' for opt in self.not_required_if])})."
        ).strip()
        super(Mutex, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        self_is_present = self.name in opts
        others_present = [
            mutex_opt for mutex_opt in self.not_required_if if mutex_opt in opts
        ]
        if self_is_present and others_present:
            raise click.UsageError(
                f"Illegal usage: --{str(self.name)} is mutually exclusive with {', '.join([f'--{opt}' for opt in self.not_required_if])}"
            )
        if self_is_present or others_present:
            self.prompt = None
        return super(Mutex, self).handle_parse_result(ctx, opts, args)
