import math

import pytest
import torch

from act_agent.training.pairwise import pairwise_objective


def test_pairwise_method_mapping_at_zero_advantage() -> None:
    zero = torch.tensor(0.0)
    assert pairwise_objective("dpo", zero, 0.1).item() == pytest.approx(math.log(2))
    assert pairwise_objective("act_pair", zero, 0.1, 3.0).item() == pytest.approx(math.log(2))
    assert pairwise_objective("act_po", zero, 0.1, 3.0).item() == pytest.approx(3 * math.log(2))
    assert pairwise_objective("ipo", zero, 0.1).item() == pytest.approx(25.0)
    assert pairwise_objective("robust_dpo", zero, 0.1).item() == pytest.approx(math.log(2))


def test_pairwise_objective_has_finite_gradient() -> None:
    advantage = torch.tensor(0.2, requires_grad=True)
    pairwise_objective("act_po", advantage, 0.1, 2.0).backward()
    assert advantage.grad is not None and torch.isfinite(advantage.grad)
