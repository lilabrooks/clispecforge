import pytest
from greeting_cli.cli import main


def test_greet_prints_name(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["Lila"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "Hello, Lila\n"
    assert captured.err == ""


def test_greet_preserves_spaces(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["Python CLI"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "Hello, Python CLI\n"


def test_greet_requires_name(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main([])

    captured = capsys.readouterr()
    assert error.value.code == 2
    assert captured.out == ""
    assert "the following arguments are required: name" in captured.err
