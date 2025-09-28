import time


def time_logger(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        res = func(*args, **kwargs)
        end_time = time.time()
        print(f"Функция {func.__name__} заняла {end_time - start_time} секунд")
        return res

    return wrapper


@time_logger
def sum_nums(a, b) -> int:
    return a + b


print(sum_nums(time_logger)(1, 2))
