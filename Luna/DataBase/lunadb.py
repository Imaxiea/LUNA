"""
Description: 对LUNA的数据库进行存取调用等操作。
"""
import sqlite3
from typing import Any
from pathlib import Path


DB_PATH = Path(__file__).parent / "luna.db"

class LunaDB:
    def __init__(self):
        with sqlite3.connect(DB_PATH) as conn:
             conn.execute("""CREATE TABLE IF NOT EXISTS calls (
                             id INTEGER,
                             input_prompt TEXT,
                             duration_ms INTEGER,
                             aioutput TEXT NOT NULL,
                             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                             )
                          """)

    @staticmethod
    def inputdb(prompt:str, duration_ms:int, output:str) -> int:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                if not [row[0] for row in conn.execute("SELECT * FROM calls WHERE id").fetchall()]:
                    conn.execute("""INSERT INTO calls (id, input_prompt, duration_ms, aioutput)
                                    values (?, ?, ?, ?)""", (1, prompt, duration_ms, output))
                else:
                    conn.execute("""INSERT INTO calls (id, input_prompt, duration_ms, aioutput)
                                    values (?, ?, ?, ?)""", (max([row[0] for row in conn.execute("SELECT * FROM calls WHERE id").fetchall()])+1, prompt, duration_ms, output))
            return 1
        except sqlite3.OperationalError or sqlite3.DatabaseError:
            return 0

    @staticmethod
    def searchdb(datatype:str='output', **kwargs) -> int | None | Any:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            try:
                if datatype == 'output':
                    result = conn.execute("SELECT aioutput FROM calls WHERE id = ?", (kwargs['id'],)).fetchone()
                    if result:
                        return result
                    else:
                        return 0
                elif datatype == 'prompt':
                    result = conn.execute("SELECT input_prompt FROM calls WHERE id = ?", (kwargs['id'],)).fetchone()
                    if result:
                        return result
                    else:
                        return 0
                elif datatype == 'time':
                    result = conn.execute("SELECT duration_ms FROM calls WHERE id = ?", (kwargs['id'],)).fetchone()
                    if result:
                        return result
                    else:
                        return 0
            except sqlite3.OperationalError:
                return -1

    @staticmethod
    def deletedb(id:int) -> bool:
        with sqlite3.connect(DB_PATH) as conn:
            try:
                conn.execute("""DELETE FROM calls WHERE id = ?""", (id,))
                return True
            except sqlite3.OperationalError:
                return False

class HashDB:
    def __init__(self):
        with sqlite3.connect(DB_PATH) as conn:
             conn.execute("""CREATE TABLE IF NOT EXISTS hashs (
                             prompt_hash TEXT NOT NULL,
                             prompt TEXT NOT NULL,
                             typ TEXT NOT NULL,
                             res TEXT NOT NULL,
                             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                             )
                          """)

    @staticmethod
    def inputdb(prompthash, prompt:str, typ:str, result:str) -> int:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("""
                             INSERT INTO hashs (prompt_hash, prompt, typ, res)""",
                             (prompthash, prompt, typ, result))
                return 1
        except sqlite3.OperationalError:
            return 0

    @staticmethod
    def searchdb(prompthash:str):
        row = conn.execute("""
                           SELECT res
                           FROM hashs
                           WHERE prompt_hash = ?
                           """, (prompthash,)).fetchone()
        if row:
            return row[3]
        return None
