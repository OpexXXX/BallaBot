import sqlite3

class SQLiteProvider:
    _conn = 0
    _curs = 0
    @staticmethod
    def connect( database) -> object:
        SQLiteProvider._conn = sqlite3.connect(database)
        SQLiteProvider._curs = SQLiteProvider._conn.cursor()
    
    @staticmethod
    def exists_user(user_id):
        return bool(SQLiteProvider._curs.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone())
    @staticmethod
    def number_of_users():
        result = (SQLiteProvider._curs.execute("SELECT Count(*) FROM users")).fetchone()[0]
        print(result)
        return  result

    @staticmethod
    def get_user_turrets(user_id):
        
        result = SQLiteProvider._curs.execute("SELECT turret_height,turret_len,click_on_turn FROM users WHERE user_id=?", (user_id,)).fetchone()
        print( result)
        return  result
    @staticmethod
    def add_to_db( user_id, first_name, last_name, username):
        SQLiteProvider._curs.execute("INSERT INTO users(user_id, first_name, last_name, username,count_of_gen) VALUES(?,?,?,?,'0')", (user_id, first_name, last_name, username))
        SQLiteProvider._conn.commit()
    
    @staticmethod
    def update_db_turr( user_id, turret_height, turret_len, click_on_turn):
        SQLiteProvider._curs.execute("UPDATE users SET  turret_height=?, turret_len=?, click_on_turn=? WHERE user_id = ?", (turret_height, turret_len, click_on_turn,user_id))
        SQLiteProvider._conn.commit()
    
    @staticmethod
    def increment_generate(user_id):
        count = int(SQLiteProvider._curs.execute("SELECT count_of_gen FROM users WHERE user_id=?", (user_id,)).fetchone()[0])
        count+=1
        print(count)
        SQLiteProvider._curs.execute("UPDATE users SET  count_of_gen=? WHERE user_id = ?", (count,user_id))
        SQLiteProvider._conn.commit()
