# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Core Decorators - 通用装饰器
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
Core Decorators 模块

提供通用的装饰器：
- retry: 自动重试
- timer: 计时
- validate: 参数验证
"""

import functools
import time
from typing import Callable, Any, Optional, Type


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    自动重试装饰器
    
    @param max_attempts: 最大重试次数
    @param delay: 重试延迟（秒）
    @param exceptions: 需要重试的异常类型
    @param on_retry: 重试回调函数
    
    使用示例：
        @retry(max_attempts=3, delay=1.0)
        def api_call():
            return requests.get("https://api.example.com")
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        if on_retry:
                            on_retry(attempt + 1, max_attempts, e)
                        time.sleep(delay)
                    else:
                        raise last_exception
            
            raise last_exception or Exception("重试失败")
        
        return wrapper
    return decorator


def timer(func: Optional[Callable] = None, *, print_time: bool = True):
    """
    计时装饰器
    
    @param func: 被装饰函数
    @param print_time: 是否打印执行时间
    
    使用示例：
        @timer
        def slow_function():
            time.sleep(1)
        
        # 或
        @timer(print_time=False)
        def another_function():
            pass
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            result = f(*args, **kwargs)
            elapsed = time.time() - start_time
            
            if print_time:
                print(f"[{f.__name__}] 执行时间: {elapsed:.3f}s")
            
            # 将执行时间附加到结果（如果是字典）
            if isinstance(result, dict):
                result["_execution_time"] = elapsed
            
            return result
        
        return wrapper
    
    if func is not None:
        return decorator(func)
    return decorator


def validate(**validators):
    """
    参数验证装饰器
    
    @param validators: 验证器字典 {参数名: 验证函数}
    
    使用示例：
        @validate(
            user_id=lambda x: x > 0,
            name=lambda x: len(x) > 0
        )
        def create_user(user_id: int, name: str):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 获取函数参数名
            import inspect
            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())
            
            # 构建参数值字典
            arg_dict = {}
            for i, arg in enumerate(args):
                if i < len(param_names):
                    arg_dict[param_names[i]] = arg
            arg_dict.update(kwargs)
            
            # 执行验证
            for param_name, validator in validators.items():
                if param_name in arg_dict:
                    value = arg_dict[param_name]
                    if not validator(value):
                        raise ValueError(
                            f"参数验证失败: {param_name}={value}"
                        )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# 导出
__all__ = ["retry", "timer", "validate"]
