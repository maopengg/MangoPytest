# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据源管理模块（带缓存）
# @Time   : 2024-04-02 9:48
# @Author : 毛鹏
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame

from core.exceptions import *
from core.sources.feishu.document_data import DocumentData


class SourcesData:
    """
    数据源管理类
    
    管理 UI 元素的获取，支持缓存：
    1. 内存缓存（类变量 _ui_element_cache）
    2. 文件缓存（本地 JSON，5分钟过期）
    3. 飞书文档（远程数据源）
    """

    ui_element: DataFrame = None
    r = DocumentData()

    # 内存缓存
    _ui_element_cache: Optional[DataFrame] = None
    _cache_time: Optional[datetime] = None

    # 缓存配置
    _CACHE_FILE = Path("cache/ui_elements.json")
    _CACHE_EXPIRE_SECONDS = 300  # 5 分钟

    @classmethod
    def get_ui_element(cls, is_dict=True, **kwargs) -> list[dict] | dict | None:
        """
        获取 UI 元素
        """
        cls.ui_element = cls._get_cached_data()
        if cls.ui_element is None:
            cls.ui_element = cls.r.ui_element().replace({np.nan: None})
            cls._save_cache(cls.ui_element)
        return cls.get(cls.ui_element, is_dict, **kwargs)

    @classmethod
    def get(cls, df: DataFrame, is_dict: bool, **kwargs) -> list[dict] | dict | None:
        # 处理重复列名：重命名重复列
        cols = pd.Series(df.columns)
        for dup in cols[cols.duplicated()].unique():
            dup_mask = cols == dup
            dup_indices = cols[dup_mask].index.tolist()
            for i, idx in enumerate(dup_indices[1:], start=1):
                cols.iloc[idx] = f"{dup}_{i}"
        df = df.copy()
        df.columns = cols
        
        conditions = None
        for key, value in kwargs.items():
            if isinstance(value, list):
                condition = df[key].isin(value)
            else:
                condition = df[key] == value
            if conditions is None:
                conditions = condition
            else:
                conditions = conditions & condition

        result = df[conditions]
        if result.empty:
            raise ToolsError(*ERROR_MSG_0349, value=(str(kwargs),))
        elif len(result) == 1:
            data = result.squeeze().to_dict()
        else:
            data = result.to_dict(orient="records")
        if isinstance(data, list) and is_dict:
            raise ToolsError(*ERROR_MSG_0348, value=(str(kwargs),))
        elif isinstance(data, list) and not is_dict:
            return data
        elif isinstance(data, dict) and is_dict:
            return data
        elif isinstance(data, dict) and not is_dict:
            return [
                data,
            ]

    @classmethod
    def _get_cached_data(cls) -> Optional[DataFrame]:
        """
        获取缓存的 UI 元素数据

        优先级：内存缓存 > 文件缓存 > None

        Returns:
            缓存的 DataFrame 或 None
        """
        # 1. 检查内存缓存
        if cls._ui_element_cache is not None and cls._cache_time is not None:
            if (datetime.now() - cls._cache_time).seconds < cls._CACHE_EXPIRE_SECONDS:
                return cls._ui_element_cache
            else:
                # 内存缓存过期
                cls._ui_element_cache = None
                cls._cache_time = None

        # 2. 检查文件缓存
        if cls._CACHE_FILE.exists():
            try:
                with open(cls._CACHE_FILE, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)

                cache_time = datetime.fromisoformat(cache_data['cache_time'])
                if (datetime.now() - cache_time).seconds < cls._CACHE_EXPIRE_SECONDS:
                    # 文件缓存有效，加载到内存
                    df = pd.DataFrame(cache_data['data'])
                    cls._ui_element_cache = df
                    cls._cache_time = cache_time
                    return df
                else:
                    # 文件缓存过期，删除
                    cls._CACHE_FILE.unlink()
            except (json.JSONDecodeError, KeyError, ValueError):
                # 缓存文件损坏，删除
                if cls._CACHE_FILE.exists():
                    cls._CACHE_FILE.unlink()

        return None

    @classmethod
    def _save_cache(cls, df: DataFrame) -> None:
        """
        保存数据到缓存

        Args:
            df: UI 元素 DataFrame
        """
        # 保存到内存
        cls._ui_element_cache = df
        cls._cache_time = datetime.now()

        # 保存到文件（使用临时文件+重命名，确保原子性写入）
        try:
            cls._CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

            # 处理重复列名问题：将 DataFrame 转换为字典列表
            # 使用 to_dict 并处理所有值使其可 JSON 序列化
            raw_data = df.to_dict('records')
            data = []
            for row in raw_data:
                row_dict = {}
                for col, value in row.items():
                    # 处理不可序列化的类型
                    if hasattr(value, 'item'):  # numpy 类型
                        try:
                            value = value.item()
                        except (ValueError, TypeError):
                            value = str(value)
                    elif pd.isna(value):  # NaN/None
                        value = None
                    elif isinstance(value, (list, tuple)):
                        # 处理列表中的 numpy 类型
                        value = [
                            v.item() if hasattr(v, 'item') else
                            None if pd.isna(v) else v
                            for v in value
                        ]

                    # 如果列名已存在，添加后缀
                    if col in row_dict:
                        suffix = 1
                        new_col = f"{col}_{suffix}"
                        while new_col in row_dict:
                            suffix += 1
                            new_col = f"{col}_{suffix}"
                        row_dict[new_col] = value
                    else:
                        row_dict[col] = value
                data.append(row_dict)

            cache_data = {
                'cache_time': datetime.now().isoformat(),
                'data': data
            }

            # 先写入临时文件，再重命名（防止写入过程中断导致文件损坏）
            temp_file = cls._CACHE_FILE.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            # 重命名为正式文件（原子操作）
            if cls._CACHE_FILE.exists():
                cls._CACHE_FILE.unlink()
            temp_file.rename(cls._CACHE_FILE)

        except Exception as e:
            # 文件缓存失败不影响使用，但打印错误便于调试
            print(f"缓存写入失败: {e}")
            pass

    @classmethod
    def clear_cache(cls) -> None:
        """
        清除缓存
        
        清除内存缓存和文件缓存
        """
        # 清除内存缓存
        cls._ui_element_cache = None
        cls._cache_time = None

        # 清除文件缓存
        if cls._CACHE_FILE.exists():
            try:
                cls._CACHE_FILE.unlink()
            except Exception:
                pass

    @classmethod
    def get_cache_info(cls) -> Optional[Dict[str, Any]]:
        """
        获取缓存信息（调试用）
        
        Returns:
            缓存信息字典
        """
        # 检查内存缓存
        if cls._ui_element_cache is not None and cls._cache_time is not None:
            elapsed = (datetime.now() - cls._cache_time).seconds
            remaining = max(0, cls._CACHE_EXPIRE_SECONDS - elapsed)
            return {
                'source': 'memory',
                'cache_time': cls._cache_time.isoformat(),
                'elapsed_seconds': elapsed,
                'remaining_seconds': remaining,
                'is_expired': elapsed >= cls._CACHE_EXPIRE_SECONDS,
                'data_count': len(cls._ui_element_cache)
            }

        # 检查文件缓存
        if cls._CACHE_FILE.exists():
            try:
                with open(cls._CACHE_FILE, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                cache_time = datetime.fromisoformat(cache_data['cache_time'])
                elapsed = (datetime.now() - cache_time).seconds
                remaining = max(0, cls._CACHE_EXPIRE_SECONDS - elapsed)
                return {
                    'source': 'file',
                    'cache_time': cache_time.isoformat(),
                    'elapsed_seconds': elapsed,
                    'remaining_seconds': remaining,
                    'is_expired': elapsed >= cls._CACHE_EXPIRE_SECONDS,
                    'data_count': len(cache_data.get('data', []))
                }
            except Exception:
                return None

        return None


if __name__ == "__main__":
    element_dict: dict = SourcesData.get_ui_element(
        项目名称='qfei_contract_ui',
        模块名称='系统管理',
        页面名称='合同类型管理',
        元素名称= '创建二级合同类型-创建成功提示',
    )
    print(element_dict)
