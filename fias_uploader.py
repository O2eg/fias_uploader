from dbfread import DBF
import asyncpg
import traceback
import os
from itertools import islice
import sys
import time
import asyncio
import aioprocessing
import math


def exception_helper(show_traceback=True):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    return "\n".join(
        [
            v for v in traceback.format_exception(exc_type, exc_value, exc_traceback if show_traceback else None)
        ]
    )


class InputData:
    data_dir = None

    fias_dicts = {
        'fias_dict_centerst': [],
        'fias_dict_currentstid': [],
        'fias_dict_eststat': [],
        'fias_dict_flattype': [],
        'fias_dict_ndoctype': [],
        'fias_dict_operstat': [],
        'fias_dict_roomtype': [],
        'fias_dict_socrbase': [],
        'fias_dict_strstat': []
    }

    fias_dict_files = {
        'fias_dict_centerst': 'CENTERST.DBF',
        'fias_dict_currentstid': 'CURENTST.DBF',
        'fias_dict_eststat': 'ESTSTAT.DBF',
        'fias_dict_flattype': 'FLATTYPE.DBF',
        'fias_dict_ndoctype': 'NDOCTYPE.DBF',
        'fias_dict_operstat': 'OPERSTAT.DBF',
        'fias_dict_roomtype': 'ROOMTYPE.DBF',
        'fias_dict_socrbase': 'SOCRBASE.DBF',
        'fias_dict_strstat': 'STRSTAT.DBF'
    }

    fias_tbls = {
        'fias_addrob': [],
        'fias_house': [],
        'fias_nordoc': [],
        'fias_room': [],
        'fias_stead': []
    }

    fias_tbls_files = {}

    @staticmethod
    def has_numbers(str):
        return any(char.isdigit() for char in str)

    def get_first_file(self, mask):
        for r, d, f in os.walk(self.data_dir):
            for file in f:
                if mask in file and self.has_numbers(file) and file.endswith('.DBF'):
                    if len(DBF(os.path.join(self.data_dir, file))) > 0:
                        return file

    def get_fias_tbl(self, file):
        for k, v in self.fias_tbls_files.items():
            if v is not None:
                if file[0:4] == v[0:4]:
                    return k

    def get_fias_tbl_keys(self, file):
        for k, v in self.fias_tbls_files.items():
            if v is not None:
                if file[0:4] == v[0:4]:
                    return self.fias_tbls[k]

    def __init__(self, data_dir, db_params, files=None, conn_num=5, insert_chunk_size=5000):
        self.data_dir = data_dir
        self.conn_num = conn_num
        self.db_params = db_params
        self.insert_chunk_size = insert_chunk_size

        self.fias_tbls_files = {
                'fias_addrob': self.get_first_file('ADDROB'),
                'fias_house': self.get_first_file('HOUSE'),
                'fias_nordoc': self.get_first_file('NORDOC'),
                'fias_room': self.get_first_file('ROOM'),
                'fias_stead': self.get_first_file('STEAD')
            }

        for d_name, f_name in self.fias_dict_files.items():
            if os.path.isfile(os.path.join(self.data_dir, f_name)):
                for rec in DBF(os.path.join(self.data_dir, f_name), lowernames=True):
                    self.fias_dicts[d_name] = (list(rec.keys()))
                    break

        for d_name, f_name in self.fias_tbls_files.items():
            if f_name is not None:
                if os.path.isfile(os.path.join(self.data_dir, f_name)):
                    for rec in DBF(os.path.join(self.data_dir, f_name), lowernames=True):
                        self.fias_tbls[d_name] = (list(rec.keys()))
                        break

        if files is None:
            self.load_files()
        else:
            self.files = files

    async def load_dicts(self):
        conn = await asyncpg.connect(
                user=self.db_params['user'],
                password=self.db_params['password'],
                database=self.db_params['database'],
                host=self.db_params['host'],
                port=self.db_params['port']
            )

        for d_name, _keys in input_data.fias_dicts.items():
            if len(_keys) == 0:
                continue
            print("Loading ============> " + d_name)
            p_insert = await conn.prepare(
                "INSERT INTO public.%s(%s) VALUES (%s)" % (
                    d_name,
                    ','.join(_keys),
                    ','.join('$' + str(n) for n, i in enumerate(_keys, start=1))
                )
            )
            for rec in DBF(os.path.join(input_data.data_dir, input_data.fias_dict_files[d_name]), lowernames=True):
                params = []
                for pp in input_data.fias_dicts[d_name]:
                    params.append(rec[pp])
                await p_insert.fetchval(*params)
        await conn.close()
    files = {}

    def load_files(self):
        if os.path.isdir(self.data_dir):
            for file in os.listdir(self.data_dir):
                if (
                        file.startswith('ADDR') or file.startswith('HOUSE') or file.startswith('NORDOC') or \
                        file.startswith('ROOM') or file.startswith('STEAD')
                ) and file.endswith('.DBF') and self.has_numbers(file):
                    self.files[file] = (self.get_fias_tbl(file), self.get_fias_tbl_keys(file))

    async def run_task(self, v, pool, file):
        start = time.time()
        tbl_name = v[0]
        tbl_keys = v[1]

        print("Loading ============> " + file)
        try:
            async with pool.acquire() as conn:
                cnt = 0
                ins_recs = []
                for rec in DBF(os.path.join(self.data_dir, file), lowernames=True):
                    params = []
                    for pp in self.fias_tbls[tbl_name]:
                        params.append(rec[pp])
                    ins_recs.append(params)
                    cnt += 1
                    if cnt % self.insert_chunk_size == 0:
                        print('%s cnt = %d' % (file, cnt))
                        await conn.copy_records_to_table(tbl_name, records=ins_recs, columns=tbl_keys)
                        ins_recs.clear()

                # push tail
                if len(ins_recs) > 0:
                    await conn.copy_records_to_table(tbl_name, records=ins_recs, columns=tbl_keys)
                    ins_recs.clear()
        except:
            print(exception_helper())
            print("===============> Failed %s" % file)

        end = time.time()
        print("Elapsed: %s [%s]" % (str(round(end - start, 2)), file))

    def load(self, name='Default'):
        print("=========> Load started [%s]" % str(name))
        start_load = time.time()

        async def run():
            tasks = set()
            pool = await asyncpg.create_pool(
                user=self.db_params['user'],
                password=self.db_params['password'],
                database=self.db_params['database'],
                host=self.db_params['host'],
                port=self.db_params['port'],
                min_size=self.conn_num,
                max_size=self.conn_num
            )
            for file, v in self.files.items():
                if len(tasks) >= self.conn_num:
                    # Wait for some upload to finish before adding a new one
                    _, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                tasks.add(loop.create_task(self.run_task(v, pool, file)))
            # Wait for the remaining uploads to finish
            await asyncio.wait(tasks)

        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(run())
        except asyncio.exceptions.TimeoutError:
            pass

        end_load = time.time()
        print("<========= Load finished, elapsed: %s [%s]" % (str(round(end_load - start_load, 2)), str(name)))
        return True


def call_load(idx, queue, event, lock, dir, target_db, files, conn_per_proc_num, insert_chunk_size):
    #with lock:
    event.set()
    input_data = InputData(
        dir, target_db, files=files, conn_num=conn_per_proc_num, insert_chunk_size=insert_chunk_size
    )
    res = input_data.load('Process %s' % idx)
    queue.put(res)
    queue.close()


@asyncio.coroutine
def run_processes(idx, queue, event, lock, dir, target_db, files, conn_per_proc_num, insert_chunk_size):
    p = aioprocessing.AioProcess(
        target=call_load, args=(idx, queue, event, lock, dir, target_db, files, conn_per_proc_num, insert_chunk_size)
    )
    p.start()
    print("===============> Process %d started" % idx)
    while True:
        result = yield from queue.coro_get()
        if result in (None, True, False):
            break
    print("<=============== Process %d finished: %s" % (idx, result))
    yield from p.coro_join()


def chunks(data, parts):
    it = iter(data)
    for i in range(0, len(data), parts):
        yield {k: data[k] for k in islice(it, parts)}


if __name__ == "__main__":
    input_dir = 'data'
    proc_num = 10
    conn_per_proc_num = 5
    insert_chunk_size = 5000

    target_db = {
        "user": 'app_user',
        "password": 'app_user',
        "database": 'fias_db',
        "host": '127.0.0.1',
        "port": '5400'
    }

    loop = asyncio.get_event_loop()
    queue = aioprocessing.AioQueue()
    event = aioprocessing.AioEvent()
    lock = aioprocessing.AioLock()

    tasks = []
    part_files = []

    start = time.time()
    input_data = InputData(input_dir, target_db)
    loop.run_until_complete(input_data.load_dicts())

    for item in chunks(input_data.files, math.ceil(len(input_data.files) / proc_num)):
        part_files.append(item)

    for idx, part in enumerate(part_files):
        tasks.append(
            asyncio.ensure_future(
                run_processes(
                    idx + 1, queue, event, lock, input_dir, target_db, part, conn_per_proc_num, insert_chunk_size
                )
            )
        )

    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    end = time.time()
    print("<========== Total elapsed: %s" % (str(round(end - start, 2))))
