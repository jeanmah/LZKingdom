import psycopg2
import LZKingdom as LZ 
from datetime import datetime, timezone
import urllib.parse as urlparse
import os

def postgresConnection():
    try:
        url = urlparse.urlparse(os.environ['DATABASE_URL'])
        dbname = url.path[1:]
        user = url.username
        password = url.password
        host = url.hostname
        port = url.port

        global connection, cursor
        connection = psycopg2.connect(dbname=dbname,
                                        user=user,
                                        password=password,
                                        host=host,
                                        port=port)
        connection.autocommit = True
        cursor = connection.cursor()

        # Executing a SQL query to insert datetime into table
        #connection.commit()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)       

def closePosgres():
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")


def insertGroupChatTable(group_chat_id:int): 
    cursor.execute(""" SELECT EXISTS(SELECT 1 from group_info where group_chat_id = %s)""", (group_chat_id,))
    does_exist = cursor.fetchone()[0]
    if(not does_exist):
        insert_query = """ INSERT INTO group_info (group_chat_id) VALUES ({0})""".format(group_chat_id)
        cursor.execute(insert_query)
        connection.commit()
        print("added group_chat to database successfully")
    else:
        print(group_chat_id,"group already in databse")

def getJoinedUsers(group_chat_id:int):
    cursor.execute("SELECT joined_users from group_info where group_chat_id = %s",(group_chat_id,))
    joined_users = cursor.fetchone()
    connection.commit()

    print("joined_users",joined_users)
    if not joined_users or not joined_users[0] :
        return []
    return joined_users[0]

def getStartTime(group_chat_id:int):
    cursor.execute("""SELECT start_time from group_info where group_chat_id = %s""",(group_chat_id,))
    start_time = cursor.fetchone()
    connection.commit()
    return start_time[0]


def updateJoinedUsers(group_chat_id:int,joined_users:list) ->None:
    cursor.execute(""" UPDATE group_info SET joined_users = %s where group_chat_id = %s""", (joined_users,group_chat_id))
    connection.commit()

def insertUserRow(user_id:int,username:str,group_chat_id:int) ->None:
    insert_query = """ INSERT INTO player_table (player_id,username,group_chat_id,doaist_score,satisfaction_score, started,attacked_by) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
    cursor.execute(insert_query,(user_id,username,group_chat_id,0,0,False,None))
    connection.commit()

    print("added user to database successfully")

def checkUserExists(user_id:int) -> bool:
    cursor.execute(""" SELECT EXISTS(SELECT 1 from player_table where player_id = %s)""", (user_id,))
    does_exist = cursor.fetchone()[0]
    connection.commit()
    print("exists",does_exist)
    return does_exist

def getGroupIdOfPlayer(player_id:int) ->int:
    cursor.execute("""SELECT group_chat_id from player_table where player_id = %s""",(player_id,))
    group_chat_id = cursor.fetchone()
    connection.commit()
    print("getGroupIdOfPlayer: "+str(group_chat_id))
    return group_chat_id[0]

def updateDaoistSatScore(user_id:int,doaist_score:int, satisfaction_score:int) -> None:
    cursor.execute(""" UPDATE player_table SET doaist_score = %s, satisfaction_score = %s where player_id = %s""", (doaist_score,satisfaction_score, user_id))
    connection.commit()

def getDaoistSatScore(user_id:int) -> None:
    cursor.execute(""" SELECT doaist_score FROM player_table where player_id = %s""", (user_id,))
    doaist_score = cursor.fetchone()
    connection.commit()
    cursor.execute(""" SELECT satisfaction_score FROM player_table where player_id = %s""", (user_id,))
    sat_score = cursor.fetchone()
    connection.commit()
    
    return (doaist_score[0],sat_score[0])

def getOtherPlayers(user_id:int) -> list:
    group_chat_id = getGroupIdOfPlayer(user_id)

    joined_users = getJoinedUsers(group_chat_id)
    ids = []
    usernames = []
    for idUsernameT in joined_users:
        idUsername = idUsernameT.split(":")
        usernames.append(idUsername[1])
        ids.append(int(idUsername[0]))
    print("ids",ids)
    print("usernames",usernames)
    selfIndex = ids.index(user_id)
    ids.pop(selfIndex)
    usernames.pop(selfIndex)
    return [ids,usernames]

def getOtherPlayerDaoistPoint(otherUsername) ->int:
    cursor.execute("SELECT doaist_score from player_table where username = %s",(otherUsername,))
    otherDaoistPoints = cursor.fetchone()
    connection.commit()
    return otherDaoistPoints[0]

def getAttackedBy(user_id:int):
    cursor.execute("SELECT attacked_by from player_table where player_id = %s",(user_id,))
    attackedBy = cursor.fetchone()
    connection.commit()

    print("attackedBy",attackedBy)
    if not attackedBy or not attackedBy[0] :
        return []
    return attackedBy[0]

def getAttackedByUsername(username:str):
    cursor.execute("SELECT attacked_by from player_table where username = %s",(username,))
    attackedBy = cursor.fetchone()
    connection.commit()

    print("attackedBy",attackedBy)
    if not attackedBy or not attackedBy[0] :
        return []
    return attackedBy[0]

def getOtherAttackedBy(username:str) ->list:
    cursor.execute("SELECT attacked_by from player_table where username = %s",(username,))
    attackedBy = cursor.fetchone()
    connection.commit()

    print("attackedBy",attackedBy)
    if not attackedBy or not attackedBy[0] :
        return []
    return attackedBy[0]

def updateAttackedBy(newList,username:str):
    cursor.execute(""" UPDATE player_table SET attacked_by = %s where username = %s""", (newList,username))
    connection.commit()

def declareWarWith(user_id,username,otheruserid):
    otherAttackedBy = getAttackedBy(otheruserid)
    print(otherAttackedBy)
    otherAttackedBy.append("{0}".format(username))
    cursor.execute(""" UPDATE player_table SET attacked_by = %s where player_id = %s""", (otherAttackedBy,otheruserid))
    connection.commit()

def removeDeclareWar(user_id,username,otherUsername):
    otherAttackedBy = getAttackedByUsername(otherUsername)
    print(otherAttackedBy)
    otherAttackedBy.pop(otherAttackedBy.index(username))
    cursor.execute(""" UPDATE player_table SET attacked_by = %s where username = %s""", (otherAttackedBy,otherUsername))
    connection.commit()

def getWantOwnDiplomacy(user_id):
    cursor.execute("SELECT want_diplomacy from player_table where player_id = %s",(user_id,))
    wantDiplomacy = cursor.fetchone()
    connection.commit()

    print("wantDiplomacy",wantDiplomacy)
    if not wantDiplomacy or not wantDiplomacy[0] :
        return []
    return wantDiplomacy[0]

def getWantOtherDiplomacy(username:str):
    cursor.execute("SELECT want_diplomacy from player_table where username = %s",(username,))
    wantDiplomacy = cursor.fetchone()
    connection.commit()

    print("wantDiplomacy",wantDiplomacy)
    if not wantDiplomacy or not wantDiplomacy[0] :
        return []
    return wantDiplomacy[0]

def updateOwnWantDiplomacy(newList,user_id):
    cursor.execute(""" UPDATE player_table SET want_diplomacy = %s where player_id = %s""", (newList,user_id))
    connection.commit()

def updateOtherWantDiplomacy(newList,username):
    cursor.execute(""" UPDATE player_table SET want_diplomacy = %s where username = %s""", (newList,username))
    connection.commit()

def getOwnAcceptDiplomacy(user_id):
    cursor.execute("SELECT accept_diplomacy from player_table where player_id = %s",(user_id,))
    accept_diplomacy = cursor.fetchone()
    connection.commit()

    print("accept_diplomacy",accept_diplomacy)
    if not accept_diplomacy or not accept_diplomacy[0] :
        return []
    return accept_diplomacy[0]

def getOtherAcceptDiplomacy(username:str):
    cursor.execute("SELECT accept_diplomacy from player_table where username = %s",(username,))
    accept_diplomacy = cursor.fetchone()
    connection.commit()

    print("accept_diplomacy",accept_diplomacy)
    if not accept_diplomacy or not accept_diplomacy[0] :
        return []
    return accept_diplomacy[0]

def updateOwnAcceptDiplomacy(newList,user_id):
    cursor.execute(""" UPDATE player_table SET accept_diplomacy = %s where player_id = %s""", (newList,user_id))
    connection.commit()

def updateOtherAcceptDiplomacy(newList,username):
    cursor.execute(""" UPDATE player_table SET accept_diplomacy = %s where username = %s""", (newList,username))
    connection.commit()

def startGameUpdate(group_chat_id:int, start_time:datetime):
    cursor.execute(""" UPDATE player_table SET started = %s where group_chat_id = %s""", (True,group_chat_id))
    connection.commit()
    cursor.execute(""" UPDATE group_info SET start_time = %s where group_chat_id = %s""", (start_time,group_chat_id))
    connection.commit()

def getStartedGame(player_id:int):
    cursor.execute("SELECT started from player_table where player_id = "+ str(player_id))
    has_started = cursor.fetchone()[0]
    connection.commit()

    print(player_id)
    print("has_started",has_started)
    return has_started
    # if not has_started:
    #     return False
    # return True

def removeStartedGame(player_id:int):
    group_chat_id = getGroupIdOfPlayer(player_id)
    cursor.execute(""" UPDATE player_table SET started = %s where group_chat_id = %s""", (False,group_chat_id))
    connection.commit()

def checkTimeout(player_id:int):
    try:
        group_chat_id = getGroupIdOfPlayer(player_id)

        start_time = getStartTime(group_chat_id)
        currentTime = datetime.now(timezone.utc)

        if ((currentTime - start_time).total_seconds() / 60.0>= LZ.TIMEOUT):
            cursor.execute(""" UPDATE player_table SET started = %s where group_chat_id = %s""", (False,group_chat_id))
            connection.commit()
            return True
    finally:
        return False

def deleteGroupAndPlayers(group_chat_id):
    print("deleting group_chat id ",group_chat_id)
    cursor.execute(""" DELETE FROM player_table WHERE group_chat_id = %s""", (group_chat_id,))
    cursor.execute(""" DELETE FROM group_info WHERE group_chat_id = %s""", (group_chat_id,))

def debugDeleteAllFromPosgres():
    cursor.execute
    cursor.execute("DELETE FROM group_info ")
    cursor.execute(" DELETE FROM player_table ")
    connection.commit()


