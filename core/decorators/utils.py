# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 工具装饰器
# @Time   : 2026-04-04
# @Author : 毛鹏
"""
工具装饰器模块

包含各种通用装饰器：
- retry: 重试装饰器
- singleton: 单例装饰器
- deprecated: 废弃警告装饰器
- timeit: 计时装饰器
- memoize: 缓存装饰器
- throttle: 节流装饰器
- validate_input: 输入验证装饰器
- log_execution: 执行日志装饰器
- async_task: 异步任务装饰器
- cache_result: 结果缓存装饰器
"""

import asyncio
import functools
import threading
import time
from collections import OrderedDict
from typing import Callable, Optional, Dict
from warnings import warn


def retry(max_attempts: int = 3, delay: float = 0, exceptions: tuple = (Exception,)):
    """
    重试装饰器

    Args:
        max_attempts: 最大重试次数
        delay: 重试间隔（秒）
        exceptions: 需要捕获的异常类型
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
            raise last_exception

        return wrapper

    return decorator


def singleton(cls):
    """
    单例装饰器

    确保类只有一个实例
    """
    instances = {}

    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def deprecated(reason: str = "This function is deprecated"):
    """
    废弃警告装饰器

    Args:
        reason: 废弃原因
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warn(f"{func.__name__} is deprecated: {reason}", DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def timeit(func: Callable = None, *, unit: str = "ms") -> Callable:
    """
    计时装饰器

    Args:
        func: 函数
        unit: 时间单位 ("s", "ms", "us")
    """

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = fn(*args, **kwargs)
            end = time.perf_counter()

            multipliers = {"s": 1, "ms": 1000, "us": 1000000}
            elapsed = (end - start) * multipliers.get(unit, 1000)

            print(f"{fn.__name__} took {elapsed:.4f} {unit}")
            return result

        return wrapper

    if func is None:
        return decorator
    return decorator(func)


def memoize(func: Callable = None, *, max_size: int = 128) -> Callable:
    """
    缓存装饰器

    Args:
        func: 函数
        max_size: 缓存最大容量
    """
    cache = OrderedDict()

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            if key in cache:
                cache.move_to_end(key)
                return cache[key]
            result = fn(*args, **kwargs)
            if len(cache) >= max_size:
                cache.popitem(last=False)
            cache[key] = result
            return result

        return wrapper

    if func is None:
        return decorator
    return decorator(func)


def throttle(interval: float = 1.0):
    """
    节流装饰器

    Args:
        interval: 最小调用间隔（秒）
    """
    last_called = {}

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = id(func)
            now = time.time()
            if key in last_called and (now - last_called[key]) < interval:
                return None
            last_called[key] = now
            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_input(**validators):
    """
    输入验证装饰器

    Args:
        validators: 参数验证器 {"param_name": validator_func}
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for param, validator in validators.items():
                if param in kwargs:
                    if not validator(kwargs[param]):
                        raise ValueError(f"Invalid value for parameter '{param}'")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_execution(logger=None, level: str = "INFO"):
    """
    执行日志装饰器

    Args:
        logger: 日志记录器
        level: 日志级别
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log = logger or print
            log_msg = getattr(log, level.lower(), log.info)
            log_msg(f"Executing {func.__name__}...")
            start = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start
                log_msg(f"Completed {func.__name__} in {elapsed:.4f}s")
                return result
            except Exception as e:
                log(f"Error in {func.__name__}: {e}")
                raise

        return wrapper

    return decorator


def async_task(func: Callable = None, *, timeout: Optional[float] = None) -> Callable:
    """
    异步任务装饰器

    Args:
        func: 异步函数
        timeout: 超时时间（秒）
    """

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if asyncio.iscoroutinefunction(fn):
                return asyncio.run(fn(*args, **kwargs))
            else:
                thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
                thread.start()
                thread.join(timeout=timeout)
                if thread.is_alive():
                    raise TimeoutError(f"Task {fn.__name__} timed out")

        return wrapper

    if func is None:
        return decorator
    return decorator(func)


def cache_result(expire_seconds: Optional[float] = None):
    """
    结果缓存装饰器（带过期时间）

    Args:
        expire_seconds: 缓存过期时间（秒）
    """
    cache: Dict[str, tuple] = {}

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{tuple(sorted(kwargs.items()))}"

            if key in cache:
                result, timestamp = cache[key]
                if expire_seconds is None or (time.time() - timestamp) < expire_seconds:
                    return result

            result = func(*args, **kwargs)
            cache[key] = (result, time.time())
            return result

        return wrapper

    return decorator


def rate_limit(max_calls: int, period: float = 1.0):
    """
    速率限制装饰器

    Args:
        max_calls: 最大调用次数
        period: 时间周期（秒）
    """
    calls = []
    lock = threading.Lock()

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                now = time.time()
                calls[:] = [t for t in calls if now - t < period]
                if len(calls) >= max_calls:
                    sleep_time = period - (now - calls[0])
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                calls.append(now)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def optional_args(func):
    """
    可选参数装饰器 - 允许不带参数调用装饰器

    Usage:
        @optional_args
        @wraps(func)
        def my_decorator(func, arg1=default1, arg2=default2):
            ...
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
