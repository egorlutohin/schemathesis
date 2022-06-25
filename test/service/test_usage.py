import click
import pytest
from click.testing import CliRunner

from schemathesis.service import usage

SCHEMA = "http://127.0.0.1:/schema.json"


@pytest.mark.parametrize(
    "args, expected",
    (
        ([SCHEMA], {"schema_kind": "URL", "parameters": {}}),
        (
            [SCHEMA, "-H='Authorization:key'", "-H='X-Key:value'"],
            {"schema_kind": "URL", "parameters": {"headers": {"count": 2}}},
        ),
        (
            [SCHEMA, "--hypothesis-max-examples=10"],
            {"schema_kind": "URL", "parameters": {"hypothesis_max_examples": {"value": "10"}}},
        ),
        (
            [SCHEMA, "--hypothesis-phases=generate"],
            {"schema_kind": "URL", "parameters": {"hypothesis_phases": {"value": "generate"}}},
        ),
        (
            [SCHEMA, "--checks=not_a_server_error", "--checks=response_conformance"],
            {
                "schema_kind": "URL",
                "parameters": {"checks": {"value": ["not_a_server_error", "response_conformance"]}},
            },
        ),
        (
            [SCHEMA, "--auth-type=digest", "--auth=user:pass"],
            {"schema_kind": "URL", "parameters": {"auth_type": {"value": "digest"}, "auth": {"count": 1}}},
        ),
    ),
)
def test_collect(args, expected):
    cli_runner = CliRunner()

    @click.command()
    def run() -> None:
        assert usage.collect(args) == expected

    result = cli_runner.invoke(run)
    assert result.exit_code == 0, result.exception


def test_collect_out_of_cli_context():
    assert usage.collect() is None
