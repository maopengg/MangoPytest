import pytest

from core.execution.catalog import ProjectCatalog


def test_catalog_discovers_project_environment_profiles(sample_project_root) -> None:
    repository_root = sample_project_root
    profiles = ProjectCatalog(repository_root).environment_profiles("sample_secondary_api")
    assert [profile["id"] for profile in profiles] == ["test"]
    assert ProjectCatalog(repository_root).environment_ids("sample_secondary_api") == ("test",)
    test_profile = profiles[0]
    assert test_profile["inherits"] == ""
    assert test_profile["summary"]["BASE_URL"] == "https://api.example.test"
    assert all("PASSWORD" not in profile["summary"] for profile in profiles)
    runtime_options = {item["key"]: item for item in test_profile["runtime_options"]}
    assert runtime_options["BASE_URL"]["value"] == "https://api.example.test"
    assert runtime_options["MOCK_TIMEOUT"]["value"] == "30"
    assert ProjectCatalog(repository_root).validate_runtime_overrides(
        "sample_secondary_api", {"BASE_URL": "https://temporary.example", "MOCK_TIMEOUT": "60"}
    ) == {"BASE_URL": "https://temporary.example", "MOCK_TIMEOUT": "60"}


def test_catalog_rejects_undeclared_or_invalid_runtime_overrides(sample_project_root) -> None:
    repository_root = sample_project_root
    catalog = ProjectCatalog(repository_root)
    with pytest.raises(ValueError, match="不允许临时覆盖"):
        catalog.validate_runtime_overrides("sample_secondary_api", {"PYTHONPATH": "/tmp/unsafe"})
    with pytest.raises(ValueError, match="http/https"):
        catalog.validate_runtime_overrides("sample_secondary_api", {"BASE_URL": "file:///tmp/mock"})
    with pytest.raises(ValueError, match="超出允许范围"):
        catalog.validate_runtime_overrides("sample_secondary_api", {"MOCK_TIMEOUT": "9999"})
