"""绑定新版 Mango Mock UI 的中文 Feature。"""

import pytest
from pytest_bdd import scenarios

pytestmark = [pytest.mark.ui, pytest.mark.positive]

scenarios(
    "../features/capabilities/operation.feature",
    "../features/capabilities/interaction.feature",
    "../features/capabilities/inventory.feature",
)
