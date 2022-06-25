import sys
from typing import Any, Dict, List, Optional, Tuple

import click
from click.types import StringParamType

from .. import cli


def collect(args: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
    """Collect anonymized CLI usage data."""
    context: Optional[click.Context] = click.get_current_context(silent=True)
    if context is not None:
        args = args or sys.argv[2:]
        parameters, _, types = parse_cli_args(context, args)
        parameters_data: Dict[str, Dict[str, Any]] = {}
        usage = {
            "schema_kind": cli.callbacks.parse_schema_kind(parameters["schema"], parameters.get("app")).name,
            "parameters": parameters_data,
        }
        types_iter = iter(types)
        for option, value in parameters.items():
            option_type = next(types_iter)
            if isinstance(option_type, click.Argument):
                continue
            if option_type.multiple:
                # Forward the iterator to the next option type
                for _ in range(len(value) - 1):
                    next(types_iter)
            entry = {}
            if isinstance(option_type.type, StringParamType):
                # Free-form values are replaced with their number of occurrences, to avoid sending
                if option_type.multiple:
                    entry["count"] = len(value)
                else:
                    entry["count"] = 1
            else:
                entry["value"] = value
            parameters_data[option] = entry
        return usage
    return None


def parse_cli_args(context: click.Context, args: List[str]) -> Tuple[Dict[str, Any], List, List[click.Parameter]]:
    parser = cli.run.make_parser(context)
    return parser.parse_args(args=args)
