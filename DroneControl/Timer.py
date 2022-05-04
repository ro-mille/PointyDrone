import ctypes
from ctypes import wintypes

class Timer():
    def __init__(self):
        self.kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        self.kernel32.QueryPerformanceFrequency.argtypes = ( wintypes.PLARGE_INTEGER, )
        self.kernel32.QueryPerformanceCounter.argtypes = ( wintypes.PLARGE_INTEGER, )

        self._qpc_frequency = wintypes.LARGE_INTEGER()
        if not self.kernel32.QueryPerformanceFrequency(ctypes.byref(self._qpc_frequency)):
            raise ctypes.WinError(ctypes.get_last_error())
        self._qpc_frequency = self._qpc_frequency.value

        self.one_second = 10000000

        self.tic = self.perf_counter_ns()
        self.toc = self.tic

    def perf_counter_ns(self):
        """perf_counter_ns() -> int

        Performance counter for benchmarking as nanoseconds.
        """
        count = wintypes.LARGE_INTEGER()
        if not self.kernel32.QueryPerformanceCounter(ctypes.byref(count)):
            raise ctypes.WinError(ctypes.get_last_error())
        return (count.value * 10 ** 7) // self._qpc_frequency

    def Restart(self):
        self.tic = self.perf_counter_ns()
        self.toc = self.tic

    def GetDelta(self):
        self.toc = self.perf_counter_ns()
        delta = self.toc - self.tic
        self.tic = self.toc
        return delta

if __name__=="__main__":
    from time import sleep
    t = Timer()
    sleep(1)
    print(t.GetDelta())
