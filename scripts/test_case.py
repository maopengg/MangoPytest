import pytest

def generate_test_cases(data):
    test_cases = []
    for item in data:
        test_name = f"test_{item['name']}"

        @pytest.mark.parametrize("input, expected", [(item['input'], item['expected'])])
        def test_func(input, expected):
            assert input == expected

        test_func.__name__ = test_name
        globals()[test_name] = test_func  # 将生成的测试用例函数添加到全局命名空间
        test_cases.append(test_func)

    return test_cases

if __name__ == '__main__':
    data = [
        {"name": "case1", "input": 1, "expected": 1},
        {"name": "case2", "input": 2, "expected": 2}
    ]

    test_cases = generate_test_cases(data)

    # 构建pytest参数列表，包括要运行的文件或模块
    args = [r'D:\GitCode\PytestAutoTest\scripts\test_case.py']

    for test_case in test_cases:
        globals()[test_case.__name__] = test_case

    pytest.main(args)
