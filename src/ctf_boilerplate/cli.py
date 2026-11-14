import os
from datetime import date
from importlib import resources
from pathlib import Path

import typer

CATEGORIES: tuple[str, ...] = ("pwn", "web", "crypto", "rev", "misc")

app = typer.Typer(
    add_completion=False,
    help="Generate a starter solve script for a CTF category.",
)


def user_template_dir() -> Path:
    """Template directory that shadows the bundled templates."""
    config_home = os.environ.get("XDG_CONFIG_HOME")
    base = Path(config_home) if config_home else Path.home() / ".config"
    return base / "ctf-boilerplate" / "templates"


def load_template(category: str, template_dir: Path | None) -> str:
    filename = f"{category}.py"
    preferred = template_dir if template_dir is not None else user_template_dir()
    path = preferred / filename
    if path.is_file():
        return path.read_text(encoding="utf-8")

    if template_dir is not None:
        raise FileNotFoundError(f"no {filename} in {template_dir}")

    return (
        resources.files("ctf_boilerplate.templates")
        .joinpath(filename)
        .read_text(encoding="utf-8")
    )


def free_path(directory: Path, stem: str) -> Path:
    candidate = directory / f"{stem}.py"
    index = 1
    while candidate.exists():
        candidate = directory / f"{stem}{index}.py"
        index += 1
    return candidate


def script_stem(name: str | None) -> str:
    stem = name or "solve"
    if stem.endswith(".py"):
        stem = stem[: -len(".py")]
    if not stem or stem in {".", ".."} or Path(stem).name != stem:
        raise ValueError(f"name must be a bare filename stem, got {name!r}")
    return stem


@app.command()
def generate(
    category: str | None = typer.Argument(
        None,
        help=f"Challenge category: {', '.join(CATEGORIES)}.",
    ),
    name: str | None = typer.Option(
        None,
        "--name",
        "-n",
        help="File stem to write instead of solve.",
    ),
    template_dir: str | None = typer.Option(
        None,
        "--template-dir",
        help="Directory to read templates from instead of the bundled ones.",
    ),
    list_categories: bool = typer.Option(
        False,
        "--list",
        is_flag=True,
        help="Print the available categories and exit.",
    ),
) -> None:
    if list_categories:
        for item in CATEGORIES:
            typer.echo(item)
        return

    if category is None:
        typer.echo(
            f"missing category; choose one of: {', '.join(CATEGORIES)}",
            err=True,
        )
        raise typer.Exit(code=2)

    if category not in CATEGORIES:
        typer.echo(
            f"unknown category {category!r}; choose one of: {', '.join(CATEGORIES)}",
            err=True,
        )
        raise typer.Exit(code=2)

    chosen_dir = Path(template_dir).expanduser() if template_dir is not None else None
    try:
        body = load_template(category, chosen_dir)
    except FileNotFoundError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error

    try:
        stem = script_stem(name)
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2) from error

    path = free_path(Path.cwd(), stem)
    header = f"# ctf-boilerplate: {category} — generated {date.today().isoformat()}\n"
    path.write_text(header + body, encoding="utf-8")
    typer.echo(os.path.relpath(path, Path.cwd()))
