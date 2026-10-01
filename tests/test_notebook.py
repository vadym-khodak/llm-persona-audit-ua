import json
import re
from pathlib import Path

import build_notebook
import collect
import design

NOTEBOOK = Path(__file__).parent.parent / "collection.ipynb"
LOCAL_MODULES = r"^\s*(import|from)\s+(design|collect|mentions|annotate|metrics|stats|report)\b"


def cells():
    return json.loads(NOTEBOOK.read_text(encoding="utf-8"))["cells"]


def test_notebook_is_up_to_date():
    assert [c["source"] for c in cells()] == [c["source"] for c in build_notebook.render()["cells"]], \
        "Запусти ../.venv/bin/python build_notebook.py"


def test_notebook_has_no_local_imports():
    for c in cells():
        if c["cell_type"] == "code":
            assert not re.search(LOCAL_MODULES, "".join(c["source"]), flags=re.M), c["source"][:3]


def test_library_cells_reproduce_modules():
    ns = {}
    for c in cells():
        if "library" in c["metadata"].get("tags", []):
            exec("".join(c["source"]), ns)
    assert ns["CONDITIONS"] == design.CONDITIONS
    assert ns["all_queries"]() == design.all_queries()
    assert ns["BRAND_ATTRS"] == design.BRAND_ATTRS
    assert {k: v["brands"] for k, v in ns["CATEGORIES"].items()} == {k: v["brands"] for k, v in design.CATEGORIES.items()}
    tasks = ns["tasks_for"]("full")
    assert tasks == collect.tasks_for("full")
    assert ns["find_mentions"]("Київстар і lifecell", ns["patterns_for"]("telecom"))[1]["brand"] == "lifecell"
