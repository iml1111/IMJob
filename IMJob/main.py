import typer

app = typer.Typer()


@app.command()
def run():
    typer.echo("Hello World")


@app.command()
def init():
    typer.echo("Hello World")


if __name__ == "__main__":
    app()
