import multiprocessing
import threading


class Singleton:
    _instance = None

    @staticmethod
    def getInstance():
        if Singleton._instance is None:
            Singleton._instance = Singleton()
        return Singleton._instance


class SharedData:
    def __init__(self, singleton):
        self.singleton = singleton


# 多线程示例
singleton = Singleton.getInstance()
shared_data = SharedData(singleton)

thread1 = threading.Thread(target=modify_singleton, args=(shared_data, 10))
thread2 = threading.Thread(target=get_singleton_value, args=(shared_data,))

thread1.start()
thread2.start()
thread1.join()
thread2.join()

# 多进程示例
if __name__ == '__main__':
    singleton = Singleton.getInstance()
    shared_data = SharedData(singleton)

    process1 = multiprocessing.Process(target=modify_singleton, args=(shared_data, 20))
    process2 = multiprocessing.Process(target=get_singleton_value, args=(shared_data,))

    process1.start()
    process2.start()
    process1.join()
    process2.join()
