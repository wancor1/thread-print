import multiprocessing as mp
import os,platform,time,atexit

ENC="shift_jis" if platform.system()=="Windows" else "utf-8"

class UltraPipePrint:
    def __init__(self,buffer_size=65536,flush_interval=0.05) -> None:
        self._parent_conn,child_conn=mp.Pipe()
        self._local_buffer=[]
        self._local_size=0
        self._buffer_size=buffer_size
        self._flush_interval=flush_interval
        self._process=mp.Process(
            target=self._worker,
            args=(child_conn,buffer_size,flush_interval),
            daemon=True
        )
        self._process.start()
        atexit.register(self.close)

    @staticmethod
    def _worker(conn,buffer_size,flush_interval) -> None:
        buffer=[]
        current_size=0
        last_flush=time.time()
        write=os.write
        fd=1
        while True:
            if conn.poll(flush_interval):
                data=conn.recv_bytes()
                if data == b"__CLOSE__":
                    break
                buffer.append(data)
                current_size+=len(data)
            now=time.time()
            if current_size >= buffer_size or (now - last_flush >= flush_interval):
                if buffer:
                    write(fd,b"".join(buffer))
                    buffer.clear()
                    current_size=0
                    last_flush=now
        if buffer: write(fd,b"".join(buffer))

    def __call__(self,*args,sep=" ",end="\n") -> None:
        msg=sep.join(map(str,args))+end
        data=msg.encode(ENC,errors="replace")
        self._local_buffer.append(data)
        self._local_size+=len(data)
        if self._local_size>=self._buffer_size:
            self._flush_local()

    def _flush_local(self) -> None:
        if not self._local_buffer: return
        try:
            self._parent_conn.send_bytes(b"".join(self._local_buffer))
        except: pass
        self._local_buffer.clear()
        self._local_size=0

    def close(self) -> None:
        if not self._process.is_alive(): return
        self._flush_local()
        try:
            self._parent_conn.send_bytes(b"__CLOSE__")
        except: pass
        self._process.join(timeout=1)
        if self._process.is_alive():
            self._process.terminate()

_instance=None
def get_async_print():
    global _instance
    if _instance is None:
        _instance=UltraPipePrint()
    return _instance
