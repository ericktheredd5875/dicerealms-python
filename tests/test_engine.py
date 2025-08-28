# SPDX-License-Identifier: MIT
# tests/test_engine.py

import pytest

from dicerealms.engine import GameEngine


def run_script(lines):
    inputs = iter(lines)
    outputs = []
    engine = GameEngine(
        input_fn=lambda: next(inputs), output_fn=lambda s: outputs.append(s)
    )
    engine.run()
    return outputs


def test_help_and_quit():
    out = run_script(["help", "quit"])
    assert any("Commands:" in line for line in out)
    assert any("Goodbye" in line for line in out)


def test_roll():
    out = run_script(["roll 1d6+0", "quit"])
    # Format check; not asserting exact number because it's random
    assert any("1d6+0" in line and "Parts:" in line for line in out)
