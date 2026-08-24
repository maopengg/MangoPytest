"""Per-test runtime data lineage collection for Factory and Repository calls."""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field
from functools import wraps
import inspect
import re
from typing import Any, Callable

from core.execution.evidence import safe_value


_CURRENT: ContextVar["DataLineageCollector | None"] = ContextVar("mango_data_lineage", default=None)
_PROTOCOL_SUFFIX = re.compile(r"_(http|mcp|grpc|ws|websocket|sse)$")


def _response_value(value: Any) -> tuple[int | None, Any]:
    status = getattr(value, "status_code", None)
    if hasattr(value, "data") and status is not None:
        return status, safe_value(value.data)
    if hasattr(value, "json") and callable(value.json):
        try:
            return status, value.json()
        except Exception:
            return status, safe_value(value)
    return status, safe_value(value)


def _payload_data(value: Any) -> Any:
    if isinstance(value, dict) and "data" in value and isinstance(value["data"], (dict, list)):
        return value["data"]
    return value


def _first_id(value: Any) -> str:
    value = _payload_data(value)
    if isinstance(value, dict):
        for key in ("id", "run_id", "job_id", "claim_id", "order_id", "product_id", "review_id"):
            if value.get(key) is not None:
                return str(value[key])
    return ""


def _references(value: Any) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key.endswith("_id") and isinstance(item, (str, int)):
                found.append((key[:-3], str(item)))
            else:
                found.extend(_references(item))
    elif isinstance(value, (list, tuple)):
        for item in value:
            found.extend(_references(item))
    return found


def _entity_type(owner: type, method_name: str) -> str:
    name = _PROTOCOL_SUFFIX.sub("", method_name.lower())
    for prefix in ("create_", "update_", "delete_", "remove_", "get_", "start_"):
        if name.startswith(prefix):
            entity_type = name[len(prefix):]
            return "test_run" if entity_type == "run" else entity_type
    if name in {"create", "update", "delete", "remove", "build"}:
        return re.sub(r"(factory|repository|repo)$", "", owner.__name__, flags=re.I).lower()
    return name


def _action(method_name: str) -> str:
    name = method_name.lower()
    if name.startswith(("delete", "remove")) or name in {"delete", "remove", "close"}:
        return "delete"
    if name.startswith(("update", "patch")) or name in {"update", "patch"}:
        return "update"
    return "create"


@dataclass
class DataLineageCollector:
    case_node_id: str
    nodes: list[dict[str, Any]] = field(default_factory=list)
    edges: list[dict[str, str]] = field(default_factory=list)
    _sequence: int = 0
    _objects: dict[int, str] = field(default_factory=dict)
    _entities: dict[tuple[str, str], str] = field(default_factory=dict)

    def _id(self, prefix: str) -> str:
        self._sequence += 1
        return f"{prefix}-{self._sequence}"

    def _node(self, *, kind: str, label: str, source: str, data: Any,
              entity_type: str = "", entity_id: str = "", status: str = "created") -> str:
        node_id = self._id(kind)
        self.nodes.append({
            "id": node_id, "kind": kind, "label": label, "source": source,
            "entity_type": entity_type, "entity_id": entity_id,
            "status": status, "data": safe_value(data),
        })
        return node_id

    def _edge(self, source: str, target: str, relation: str) -> None:
        if source and target and not any(
            edge["source"] == source and edge["target"] == target and edge["relation"] == relation
            for edge in self.edges
        ):
            self.edges.append({"source": source, "target": target, "relation": relation})

    def factory(self, owner: type, method_name: str, result: Any) -> None:
        entity_type = _entity_type(owner, method_name)
        node_id = self._node(
            kind="factory", label=f"{owner.__name__}.{method_name}",
            source=f"{owner.__module__}.{owner.__name__}", data=result,
            entity_type=entity_type,
        )
        if not isinstance(result, (str, bytes, int, float, bool, type(None))):
            self._objects[id(result)] = node_id

    def repository(self, owner: type, method_name: str, args: tuple[Any, ...],
                   kwargs: dict[str, Any], result: Any = None, error: Exception | None = None,
                   related_values: tuple[Any, ...] = ()) -> None:
        action = _action(method_name)
        entity_type = _entity_type(owner, method_name)
        inputs = {"arguments": safe_value(list(args)), "keyword_arguments": safe_value(kwargs)}
        status_code, response = _response_value(result)
        succeeded = error is None and (status_code is None or 200 <= status_code < 400)
        operation_id = self._node(
            kind="operation", label=f"{owner.__name__}.{method_name}",
            source=f"{owner.__module__}.{owner.__name__}",
            entity_type=entity_type, status="passed" if succeeded else "failed",
            data={"action": action, "inputs": inputs, "status_code": status_code,
                  "response": response, "error": str(error) if error else ""},
        )
        for value in (*args, *kwargs.values(), *related_values):
            factory_id = self._objects.get(id(value))
            if factory_id:
                self._edge(factory_id, operation_id, "作为输入")

        serialized_inputs = safe_value([list(args), kwargs])
        for ref_type, ref_id in _references(serialized_inputs):
            referenced = self._entities.get((ref_type, ref_id))
            if referenced:
                self._edge(referenced, operation_id, "被引用")

        entity_id = _first_id(response) or _first_id(serialized_inputs)
        entity_key = (entity_type, entity_id)
        entity_node = self._entities.get(entity_key) if entity_id else None
        if action == "create" and succeeded:
            entity_node = self._node(
                kind="entity", label=entity_type.replace("_", " ").title(),
                source=owner.__name__, data=_payload_data(response), entity_type=entity_type,
                entity_id=entity_id, status="active",
            )
            if entity_id:
                self._entities[entity_key] = entity_node
            self._edge(operation_id, entity_node, "创建")
        elif entity_node:
            self._edge(operation_id, entity_node, "删除" if action == "delete" else "更新")
            if action == "delete" and succeeded:
                for node in self.nodes:
                    if node["id"] == entity_node:
                        node["status"] = "deleted"
                        break

    def export(self) -> dict[str, Any]:
        return {
            "version": 1,
            "case_node_id": self.case_node_id,
            "summary": {
                "factories": sum(node["kind"] == "factory" for node in self.nodes),
                "operations": sum(node["kind"] == "operation" for node in self.nodes),
                "entities": sum(node["kind"] == "entity" for node in self.nodes),
                "relations": len(self.edges),
            },
            "nodes": self.nodes,
            "edges": self.edges,
        }


def start_lineage(case_node_id: str) -> DataLineageCollector:
    collector = DataLineageCollector(case_node_id)
    _CURRENT.set(collector)
    return collector


def current_lineage() -> DataLineageCollector | None:
    return _CURRENT.get()


def stop_lineage() -> None:
    _CURRENT.set(None)


def _wrap(owner: type, name: str, function: Callable, kind: str) -> Callable:
    if getattr(function, "__mango_lineage__", False):
        return function

    @wraps(function)
    def wrapped(*args, **kwargs):
        collector = current_lineage()
        instance = args[0] if args and isinstance(args[0], owner) else None
        related_values = tuple(vars(instance).values()) if instance is not None else ()
        try:
            result = function(*args, **kwargs)
        except Exception as error:
            if collector and kind == "repository":
                call_args = args[1:] if args and isinstance(args[0], owner) else args
                collector.repository(
                    owner, name, call_args, kwargs, error=error, related_values=related_values
                )
            raise
        if collector:
            call_args = args[1:] if args and isinstance(args[0], owner) else args
            if kind == "factory":
                collector.factory(owner, name, result)
            else:
                collector.repository(
                    owner, name, call_args, kwargs, result=result, related_values=related_values
                )
        return result

    wrapped.__mango_lineage__ = True
    return wrapped


def instrument_lineage_object(value: Any) -> None:
    """Instrument returned Factory/Repository fixtures once, without project coupling."""
    if value is None:
        return
    owner = type(value)
    module = owner.__module__.lower()
    if "data_factory.factories" in module or owner.__name__.endswith("Factory"):
        kind = "factory"
    elif ".repositories." in module or ".repos." in module or owner.__name__.endswith(("Repository", "Repo")):
        kind = "repository"
    else:
        return
    if owner.__dict__.get("__mango_lineage_instrumented__"):
        return
    for name, descriptor in tuple(owner.__dict__.items()):
        if name.startswith("_") or name in {"unique", "headers", "data", "current_token"}:
            continue
        if kind == "repository" and not (
            name.startswith(("create", "update", "delete", "remove", "start"))
            or name in {"create", "update", "delete", "remove", "close"}
        ):
            continue
        if isinstance(descriptor, staticmethod):
            setattr(owner, name, staticmethod(_wrap(owner, name, descriptor.__func__, kind)))
        elif isinstance(descriptor, classmethod):
            setattr(owner, name, classmethod(_wrap(owner, name, descriptor.__func__, kind)))
        elif inspect.isfunction(descriptor):
            setattr(owner, name, _wrap(owner, name, descriptor, kind))
    owner.__mango_lineage_instrumented__ = True
