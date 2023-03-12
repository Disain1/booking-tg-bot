import utils.status as status

from utils.database import Database


def initDatabase(db: Database):
    db.commit("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY, name TEXT, from_petrsu BOOLEAN, vk_id TEXT)")
    db.commit("CREATE TABLE IF NOT EXISTS states(user_id INTEGER PRIMARY KEY, state INTEGER)")
    db.commit("CREATE TABLE IF NOT EXISTS places(user_id INTEGER DEFAULT NULL, row INTEGER, place INTEGER, status INTEGER)")

    c = db.getOne("SELECT count(*) FROM places")[0]
    if c == 0: # если в базе нет информации о местах
        for place in range(1, 22+1): # добавляем 1 ряд
            db.commit("INSERT INTO places VALUES(?, ?, ?, ?)", [None, 1, place, status.FREE])

        for row in range(2, 17+1): # добавляем со 2 по 17 ряды
            for place in range(1, 24+1):
                db.commit("INSERT INTO places VALUES(?, ?, ?, ?)", [None, row, place, status.FREE])

        for place in range(1, 10+1): # добавляем 18 ряд
            db.commit("INSERT INTO places VALUES(?, ?, ?, ?)", [None, 18, place, status.FREE])

        for place in range(1, 5+1): # добавляем 19 ряд
            db.commit("INSERT INTO places VALUES(?, ?, ?, ?)", [None, 19, place, status.FREE])

    db.commit("UPDATE places SET user_id = ?, status = ? WHERE row = 1", [0, status.OCCUPIED])
    db.commit("UPDATE places SET user_id = ?, status = ? WHERE row = 2", [0, status.OCCUPIED])
    db.commit("UPDATE places SET user_id = ?, status = ? WHERE row = 3", [0, status.OCCUPIED])


def getUserState(db: Database, user_id: int):
    result = db.getOne("SELECT state FROM states WHERE user_id = ?", [user_id])
    if result != None:
        return result[0]


def setUserState(db: Database, user_id: int, state: int):
    db.commit("UPDATE states SET state = ? WHERE user_id = ?", [state, user_id])


def removeBooking(db: Database, row: int, place: int):
    db.commit("UPDATE places SET user_id = ?, status = ? WHERE row = ? AND place = ?", [None, status.FREE, row, place])


def addBooking(db: Database, user_id: int, row: int, place: int, status: int):
    db.commit("UPDATE places SET user_id = ?, status = ? WHERE row = ? AND place = ?", [user_id, status, row, place])


def getFreePlaceNumbers(db: Database):
    return db.getAll("SELECT row, count(*) FROM places WHERE status = 0 GROUP BY row")
    