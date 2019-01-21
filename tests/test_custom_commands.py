from inspect import cleandoc
from os.path import join

import pytest

from boca import create_cli
from boca.custom import CUSTOM_COMMANDS_ENV_VAR

from .utils import env


def test_init_custom_commands_in_dir(runner, tmpdir):
    cli = create_cli()

    result = runner.invoke(cli, ["init:custom", "-d", str(tmpdir)])
    output = result.output.lower()

    assert result.exit_code == 0, output

    for item in "generated", "open the file":
        assert item in output

    with open(join(str(tmpdir), "boca.py"), "r") as generated:
        assert "import click" in generated.read()


@pytest.fixture
def custom_commands(tmpdir):
    file_ = tmpdir.join("boca.py")
    file_.write(
        cleandoc(
            """
    import click

    @click.group()
    def animals():
        pass

    @animals.command()
    def cats():
        click.echo("Cats!")

    @click.command(name="the-cars")
    def cars():
        click.echo("Cars!")
    """
        )
    )
    return str(file_)


@pytest.mark.parametrize(
    "command, exit_code, sample",
    [
        (["animals"], 0, "Usage: boca animals"),
        (["cats"], 0, "Cats!"),
        (["the-cars"], 0, "Cars!"),
        (["cars"], 2, "Usage: boca"),
    ],
)
def test_can_provide_custom_commands(
    runner, custom_commands, command, exit_code, sample
):
    with env(CUSTOM_COMMANDS_ENV_VAR, custom_commands):
        cli = create_cli()

    result = runner.invoke(cli, command)
    assert result.exit_code == exit_code
    assert sample in result.output


def test_no_commands_allowed(tmpdir):
    boca_dot_py = tmpdir.join("boca.py")
    boca_dot_py.write("import click")
    create_cli()
