"""原生 Fixture 装配 factory-boy，验证 ORM 持久化与 Repository 清理。"""

from types import ModuleType
import sys

import factory
import pytest
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from core.base.base_factory import BaseFactory
from core.base.repository_base import BaseRepository


@pytest.fixture
def factory_context(monkeypatch):
    base = declarative_base()

    class ExampleEntity(base):
        __tablename__ = "factory_example"
        id = Column(Integer, primary_key=True)
        name = Column(String, nullable=False)

    engine = create_engine("sqlite+pysqlite:///:memory:")
    base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    settings = ModuleType("example_factory_settings")
    settings.SessionLocal = lambda: session
    monkeypatch.setitem(sys.modules, settings.__name__, settings)

    class ExampleFactory(BaseFactory):
        class Meta:
            model = ExampleEntity

        _settings_module = settings.__name__
        name = factory.Sequence(lambda number: f"AUTO_factory_{number}")

    class ExampleRepository(BaseRepository):
        model = ExampleEntity
        CODE_FIELD = "name"

    try:
        yield ExampleFactory, ExampleRepository(session)
    finally:
        session.close()
        engine.dispose()


def test_native_fixture_builds_entity_without_writing_database(factory_context):
    data_factory, repository = factory_context
    entity = data_factory.build()
    assert entity.name.startswith("AUTO_")
    assert entity.id is None
    assert repository.count() == 0


def test_native_fixture_creates_queries_and_cleans_data(factory_context):
    data_factory, repository = factory_context
    entity = data_factory.create()
    assert repository.get_by_id(entity.id).name == entity.name
    assert repository.count() == 1
    assert repository.delete_auto_test_data() == 1
    assert repository.count() == 0
