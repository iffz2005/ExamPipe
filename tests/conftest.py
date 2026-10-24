from pathlib import Path

import pytest

from exampipe.config import load_course
from exampipe.sample import clean_rows

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def course():
    return load_course(ROOT / "configs" / "demo_exam.yaml")


@pytest.fixture()
def row():
    """A fresh, valid row (question 1) that tests can mutate."""
    return clean_rows()[0]
