import threading

reader_semaphore = threading.Semaphore()
mutex = threading.Lock()
read_count = 0

read_count_lock = threading.Lock()
