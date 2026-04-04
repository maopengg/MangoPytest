from multiprocessing import Process, Manager


def f(shared_dict):
    shared_dict['key'] = 'value'  # 修改共享字典


if __name__ == '__main__':
    manager = Manager()
    shared_dict = manager.dict()  # 创建一个共享字典

    p = Process(target=f, args=(shared_dict,))
    p.start()
    p.join()

    print(f'共享的字典: {shared_dict}')
