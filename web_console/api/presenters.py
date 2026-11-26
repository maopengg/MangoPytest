from core.execution.secrets import redact_overrides


def public_run(record: dict | None) -> dict | None:
    """对外返回运行记录前，对敏感运行参数脱敏。

    只在"对外"边界脱敏：执行链路会从数据库读回 ``runtime_overrides`` 重新构造子进程
    环境（``run_service._run_process``），因此写入侧必须保留原值。
    """

    if not record:
        return record
    overrides = record.get("runtime_overrides")
    if not overrides:
        return record
    return {**record, "runtime_overrides": redact_overrides(overrides)}
