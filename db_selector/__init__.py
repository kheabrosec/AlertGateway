def selectDB(db):
    f = open("db_selector/running_db","w+")
    f.write(db)
    return True
def getDB():
    try:
        f = open("db_selector/running_db","r")
        line = f.readline()
        return line.replace("\n","")
    except:
        return False