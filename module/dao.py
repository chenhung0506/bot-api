import log
import utils
# import OperationalError

log = log.logging.getLogger(__name__)


class Database(object):
    def __init__(self, conn):
        self.conn = conn

    def executeScriptsFromFile(self, filename):
        fd = open(filename, 'r')
        sqlFile = fd.read()
        fd.close()
        sqlCommands = sqlFile.split(';')

        cursor = self.conn.cursor()
        for command in sqlCommands:
            log.info(command)
            try:
                cursor.execute(command)
            # except OperationalError, msg:
            #     log.info("Command skipped: " + msg)
            except Exception as e:
                log.info(e)
                raise e

    def query_bot_work_list(self, bot_id):
        cursor = self.conn.cursor()
        try:
            if bot_id == None:
                cursor.execute("SELECT * FROM hualien.bot_work_list;")
            else:
                cursor.execute("SELECT * FROM hualien.bot_work_list WHERE bot_id = %s;", bot_id)
            data = cursor.fetchall()
            return data
        except Exception as e:
            raise e
    
    def insert_bot_work_list(self,record):
        cursor = self.conn.cursor()
        log.info(record)

        sql = "INSERT INTO hualien.bot_work_list (bot_id, work, return_flag, return_finish, edit_date) VALUES ( %s, %d, %d, %d, CURRENT_TIMESTAMP()) " + \
                "ON DUPLICATE KEY UPDATE work = %d, return_flag = %d, return_finish = %d, edit_date=CURRENT_TIMESTAMP();"
        val = (record['bot_id'], record['work'], record['return_flag'], record['return_finish'], record['work'], record['return_flag'], record['return_finish'])
        try:
            cursor.execute(self.execute_sql(sql,val))
        except Exception as e:
            log.info(self.execute_sql(sql,val))
            log.info(utils.except_raise(e))
            self.conn.rollback()
            raise e
        log.info("insert success bot_id: " + record['bot_id'])
        self.conn.commit()
        return cursor.rowcount

    def execute_sql(self, sql, values):
        unique = "%PARAMETER%"
        sql = sql.replace("?", unique)
        sql = sql.replace("%s", unique)
        sql = sql.replace("%d", unique)
        for v in values: sql = sql.replace(unique, repr(v), 1)
        return sql

    def insert_work_to_bot_work_list(self,record):
        cursor = self.conn.cursor()
        log.info(record)

        sql = "INSERT INTO hualien.bot_work_list (bot_id, work, edit_date) VALUES ( %s, %d, CURRENT_TIMESTAMP()) " + \
                "ON DUPLICATE KEY UPDATE work = %d, edit_date=CURRENT_TIMESTAMP();"
        val = (record['bot_id'], record['work'], record['work'])
        try:
            cursor.execute(self.execute_sql(sql,val))
        except Exception as e:
            log.info(self.execute_sql(sql,val))
            log.info(utils.except_raise(e))
            self.conn.rollback()
            raise e
        log.info("insert success bot_id: " + record['bot_id'])
        self.conn.commit()
        return cursor.rowcount