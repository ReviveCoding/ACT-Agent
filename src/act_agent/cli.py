"""Command line interface."""

import os
from pathlib import Path

import typer

from act_agent.data.pipeline import profile, scan
from act_agent.data.pipeline import verify as verify_source
from act_agent.evidence.release import PROTOCOL, run_all
from act_agent.evidence.verify import verify_release

app = typer.Typer(no_args_is_help=True)
data_app = typer.Typer(no_args_is_help=True)
app.add_typer(data_app, name="data")


def root() -> Path:
    return Path.cwd()


def raw() -> Path:
    return (
        Path(os.environ.get("ACT_AGENT_SCRATCH", "/home/bjw-0/.cache/act-agent-v1"))
        / "data/criteo_attribution_dataset.tsv.gz"
    )


@data_app.command("scan")
def data_scan() -> None:
    typer.echo(scan(raw()))


@data_app.command("verify")
def data_verify() -> None:
    typer.echo(verify_source(raw()))


@data_app.command("profile")
def data_profile() -> None:
    typer.echo(profile(raw(), root() / "data/processed", raw().parent.parent / "tmp"))


@app.command("run-all")
def all_stages(protocol: str = PROTOCOL, device: str = "cuda", resume: bool = True) -> None:
    if protocol != PROTOCOL or device != "cuda":
        raise typer.BadParameter("this release requires the frozen protocol and CUDA device")
    typer.echo(run_all(root(), resume))


@app.command("verify")
def verify() -> None:
    result = verify_release(root())
    typer.echo(result)
    if not result["pass"]:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
