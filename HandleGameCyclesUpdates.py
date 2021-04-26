from telegram.ext import  Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import logging

import KingdomResources as KR
import indivKingdomLogic as indivK
import HandleInfrActOptions as InfraActOpt
import HandleOtherActOptions as OtherActOpt
import HandleRandomEvents as RandOpts
import HandleWarOptions as WarOpt


import postgresqlCommands as pgres
import copy
import random

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

#CYCLE VARIABLES 
CURRENTCYCLE = "CURRENTCYCLE" #int
DAOISTCYCLETRACKER = "DAOISTCYCLETRACKER" #dictionary {id: (atCycle, +-daoistpoints)}
SATISFACTIONCYCLETRACKER = "SATISFACTIONCYCLETRACKER" #dictionary {id: (UntilCycleNum, +-satisfactionpoints)}
WARCYCLETRACKER = "WARCYCLETRACKER" #dictionary {warname: untilCycle}

def doNextRound(update: Update, _: CallbackContext, oldValues:dict, newValues:dict):
    #check if wars have ended 
    num_villagers = _.user_data["Num Villagers"]
    kingdomMoney = _.user_data["Kingdom Money"]
    daoist_points = _.user_data["Points"]
    military = _.user_data["Military Power"]
    Beauty = _.user_data["Beauty"]
    sat = _.user_data["People Satisfaction"]
    tax_amt = _.user_data["Tax Amount"]
    ave_earnings = _.user_data["Ave Villagers Earnings"]
    declare_with = _.user_data["Declared War With"]
    attacked_by = _.user_data["Being Attacked By"]
    land_amt = _.user_data["Amt Of Land"]
    values = _.user_data["Values Promoted"]

    oldValues["Num Villagers"] = num_villagers
    oldValues["Kingdom Money"] = kingdomMoney
    oldValues["Points"] = daoist_points
    oldValues["People Satisfaction"] = sat
    oldValues["Being Attacked By"] = attacked_by
    oldValues["Amt Of Land"] = land_amt

    currentCycle = _.user_data[CURRENTCYCLE]

    warCycles = _.user_data[WARCYCLETRACKER]
    war_removing_keys = []

    player_id = update.effective_chat.id

    #check lose against another player 
    try:
        for d in declare_with:
            if d not in KR.staticKingdomDict:
                otherDaoist_points = pgres.getOtherPlayerDaoistPoint(d)
                if(otherDaoist_points-daoist_points>=150):
                    return loseGame(update,_,d)

        #static kingdom wars 
        if(military>= 500 and daoist_points >= 1100):
            #wars with static kingdoms are won 
            for d in declare_with:
                if d in KR.staticKingdomDict:
                    
                    war_removing_keys.append(d)
        if(daoist_points<100 and len(declare_with) >0):
            return loseGame(update,_,"everyone you declared war to")

        for war in warCycles:
            if(warCycles[war]<=currentCycle):
                war_removing_keys.append(war)

        for key in war_removing_keys:
            warCycles.pop(key,None)
            declare_with.pop(declare_with.index(key))
            staticKingdom = KR.staticKingdomDict[key]
            land_amt +=staticKingdom.landArea
            num_villagers +=staticKingdom.numPeople

        _.user_data[WARCYCLETRACKER] =warCycles
        _.user_data["Amt Of Land"] = land_amt    

        acceptedDiplomacyKingdoms = pgres.getOwnAcceptDiplomacy(player_id)
        print("acceptdiplomacy",acceptedDiplomacyKingdoms)
        if(len(acceptedDiplomacyKingdoms)):
            for k in acceptedDiplomacyKingdoms:
                startedDiplomacyWith =  _.user_data[WarOpt.STARTEDDIPLOMACY]
                startedDiplomacyWith.pop(startedDiplomacyWith.index(k))
                _.user_data[WarOpt.STARTEDDIPLOMACY] = startedDiplomacyWith
                attacked_by.pop()


        #increase kingdom money if 
        if(currentCycle%5==0):
            militaryFraction = _.user_data["Increase Military Spending"]
            kingdomMoney += tax_amt*num_villagers*(1-militaryFraction)
            kingdomMoney = int(kingdomMoney)
            _.user_data["Kingdom Money"] = kingdomMoney

        #modify daoist points
        daoistCycle = _.user_data[DAOISTCYCLETRACKER]
        #dictionary {id: (atCycle, +-daoistpoints)}

        removing_keys = []
        for dCycle in daoistCycle:
            untilCycleNum = daoistCycle[dCycle][0]
            if(currentCycle==untilCycleNum):
                daoist_points +=daoistCycle[dCycle][1]
                print(dCycle,daoistCycle[dCycle])
                removing_keys.append(dCycle)

        for k in removing_keys:
            daoistCycle.pop(k,None)
        _.user_data[DAOISTCYCLETRACKER] = daoistCycle
        
        if(len(declare_with)):
            daoist_points-=20

        satisfactionCycle = _.user_data[SATISFACTIONCYCLETRACKER]
        
        sat = calcSatisfaction(_,satisfactionCycle,daoist_points,tax_amt,ave_earnings,currentCycle,  
            declare_with, land_amt,Beauty,military,values)

        num_villagers += getRandVillagersMoving(sat)

        if(num_villagers<=0):
            return loseGame(update,_,d)

        _.user_data["Num Villagers"] = num_villagers
        _.user_data["People Satisfaction"] = sat
        _.user_data["Points"] = daoist_points

        currentCycle+=1
        #increment cycle
        _.user_data[CURRENTCYCLE] = currentCycle


        print("from user:", player_id)
        attackedByDB = pgres.getAttackedBy(player_id)

        if(attackedByDB != attacked_by): 
            print(attackedByDB,attacked_by)
            print("different")
            _.user_data["Being Attacked By"] = attackedByDB

        pgres.updateDaoistSatScore(player_id,daoist_points,sat)

        #Check if the game has ended 

        if(not pgres.getStartedGame(player_id) or pgres.checkTimeout(player_id)):
            return neutralEndGame(update,_)
    except Exception as e: 
        print(e)
        logger.debug("Cannot find the player in table, assume game ended")
        return neutralEndGame(update,_)


    if(len(war_removing_keys)):
        return wonWarEvent(update,_,war_removing_keys)

    randomEventAvailable = _.user_data[RandOpts.AVAILABLEEVENTS]
    if(len(randomEventAvailable)):
        eventRanNum = random.randint(1,5)
        print("eventRanNum",eventRanNum)
        if(eventRanNum%5==0):
            return RandOpts.randomEventsOptions(update,_)

    newValues["Num Villagers"] = num_villagers
    newValues["Kingdom Money"] = kingdomMoney
    newValues["Points"] = daoist_points
    newValues["People Satisfaction"] = sat
    newValues["Being Attacked By"] = attackedByDB
    newValues["Amt Of Land"] = land_amt


    return cycleUpdatesOptions(update,_, oldValues, newValues,currentCycle, war_removing_keys,acceptedDiplomacyKingdoms)

def calcSatisfaction(callbackContext: CallbackContext,satisfactionCycle:dict,daoist_points:int,tax_amt:int,ave_earnings:int,currentCycle:int, 
    declare_with:list, land_amt:int,Beauty:int,military:int,values:list):
    #modify satisfaction 
    #dictionary {id: (UntilCycleNum, +-satisfactionpoints)}

    sat = daoist_points* 0.25
    if (tax_amt>=ave_earnings):
        sat-= 5

    removing_keys = []
    for satCycle in satisfactionCycle:
        untilCycleNum = satisfactionCycle[satCycle][0]
        if(currentCycle<=untilCycleNum):
            sat +=satisfactionCycle[satCycle][0]
        else:
            removing_keys.append(satCycle)
    for k in removing_keys:
        satisfactionCycle.pop(k,None)
    callbackContext.user_data[SATISFACTIONCYCLETRACKER] = satisfactionCycle

    #villagers are ok with expanding if its not too much
    if len(declare_with) and land_amt<300:
        sat -=10*len(declare_with)
    if Beauty<1000:
        sat+=Beauty/100
    if military<1500:
        sat+=military/150
    if land_amt<1000:
        sat+=land_amt/100
    if military>1500:
        sat-=military/200
    
    #higher schools bad 
    if callbackContext.user_data[KR.infraDict["Higher schools"].infraName]:
        sat-= 5

    if len(values)>0:
        sat-=len(values)*5

    print("satification before cutting", sat)
    #bound satisfaction 
    sat = int(min(400,sat))
    sat = max(0,sat)

    return sat


def getRandVillagersMoving(statisfactionPoints:int) ->int:
    satVariable = KR.statsDict["PeopleSatisfaction"]
    maxPoints = list(satVariable.categoryMax.values())
    if statisfactionPoints<maxPoints[0]: # very disastisfied
        return random.randint(1, 4)
    elif statisfactionPoints<maxPoints[2]: # disastisfied
        return random.randint(1, 3)
    elif statisfactionPoints<maxPoints[3]: # indif
        return random.randint(-1, 1)
    elif statisfactionPoints<=maxPoints[4]: # satisfied
        return random.randint(1, 3)
    else:
        return 0
    

def endGame(update: Update, _: CallbackContext, user_id):
    query = update.callback_query
    pgres.removeStartedGame(user_id)
    indivK.removeGameVariables(query.from_user.id,_)


def endGameConvHandler(update: Update, _: CallbackContext, messageToEnd:str) -> int:
    query = update.callback_query
    query.answer()

    endMessage = u'🏰*Game Ended*'
    endMessage+="\n\n{0}".format(messageToEnd)

    endMessage+="\n\nThese are your final stats\n"
    endMessage += "{0}\n\n{1}".format(indivK.getStatsMessage(_),indivK.getInfraMessage(_))
    endMessage+="\n\nHead back to the group chat to see who won"

    query.edit_message_text(text=endMessage,parse_mode= 'Markdown')
    endGame(update,_,query.from_user.id)
    return ConversationHandler.END

def loseGame(update: Update, _: CallbackContext, lostTo:str) -> int:
    endMessage="You lost a war with {0}".format(lostTo)
    #alert group
    _.bot.sendMessage(chat_id = pgres.getGroupIdOfPlayer(update.effective_message.chat_id),text="The game has ended, please send /get_rankings to get the rankings")
    endGameConvHandler(update,_,endMessage)

def neutralEndGame(update: Update, _: CallbackContext):
    endMessage="Game Timeout / Another Player has Lost"
    endGameConvHandler(update,_,endMessage)

def cycleUpdatesOptions(update: Update, _: CallbackContext, oldValues:dict, newValues:dict, currentCycle:int, warsWon:list, acceptDiplomacy:list) -> int:
    query = update.callback_query
    query.answer()
    logger.info("Cycle Update")

    statUpdateMessage = u"*What Changed📒*"
    statUpdateMessage +="\n"
    has_changes = False
    if(len((warsWon))):
        for k in warsWon:
            statUpdateMessage+="\n*The war with {0} has been won*\n".format(k)

    if(len((acceptDiplomacy))):
        for k in acceptDiplomacy:
            statUpdateMessage+="\n*{0} has accepted your diplomacy*\n".format(k)


    for keys in oldValues:
        if isinstance(newValues[keys],list):
            if(oldValues[keys] !=newValues[keys]):
                has_changes = True
                statUpdateMessage+="\n*{0}*: ".format(keys)
                statUpdateMessage+="{}".format(', '.join(oldValues[keys]))
                if(len(oldValues[keys])==0):
                    statUpdateMessage+="None"
                statUpdateMessage+= u' ➡️ '
                statUpdateMessage+="{}".format(', '.join(newValues[keys]))
                if(len(newValues[keys])==0):
                    statUpdateMessage+="None"
                statUpdateMessage +="\n"

        else:
            if(oldValues[keys] !=newValues[keys]):
                has_changes = True
                statUpdateMessage+="\n*{0}*: ".format(keys)
                statUpdateMessage+="{}".format(oldValues[keys])
                statUpdateMessage+= u' ➡️ '
                statUpdateMessage+="{}".format(newValues[keys])
                if(isinstance(oldValues[keys],int)):
                    if(newValues[keys]>oldValues[keys]):
                        statUpdateMessage+= u' ⬆️ '
                    else:
                        statUpdateMessage+= u' ⬇️ '
                statUpdateMessage +="\n"

    if not has_changes:
        statUpdateMessage+="\n~Nothing~"

    statUpdateMessage+="\n*Current Cycle: *{0}".format(currentCycle)
    keyboard = [[InlineKeyboardButton("Back to Home", callback_data=str(indivK.BACKHOME))]]    
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        text=statUpdateMessage, reply_markup=reply_markup,parse_mode= 'Markdown'
    )

    return indivK.CYCLEUPDATE

def wonWarEvent(update: Update, _: CallbackContext,warsWon:list):
    query = update.callback_query
    query.answer()

    warWonMessage = "*A WAR HAS BEEN WON*"
    warWonMessage +="\n\nYou have won the war against {}".format(', '.join(warsWon))
        
    warWonMessage += "\n\nYour villages are anticipating an end of war announcement.\n\nWhat do you declare?"
    
    keyboard = []
    for i in range(len(KR.EndOfWarOptions)):
        keyboard.append([InlineKeyboardButton("{}".format(KR.EndOfWarOptions[i]), callback_data=str(i))])
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        text=warWonMessage, reply_markup=reply_markup,parse_mode= 'Markdown'
    )

    return indivK.ENDOFWAREVENT


def updateDaoistScore(update: Update, _: CallbackContext,additionalScore:int):
    _.user_data["Points"] += additionalScore

def modifyDaoistCycleTracker(update: Update, _: CallbackContext,dictKey, numCyclesAhead, points):
    currentCycle = _.user_data[CURRENTCYCLE]
    _.user_data[DAOISTCYCLETRACKER][dictKey] = (numCyclesAhead+currentCycle,points)

def modifySatCycleTracker(update: Update, _: CallbackContext,dictKey, numCyclesAhead, points):
    currentCycle = _.user_data[CURRENTCYCLE]
    _.user_data[SATISFACTIONCYCLETRACKER][dictKey] = (numCyclesAhead+currentCycle,points)

def modifyWarCycleTracker(update: Update, _: CallbackContext,warName, numCyclesAhead):
    currentCycle = _.user_data[CURRENTCYCLE]
    _.user_data[WARCYCLETRACKER][warName] = numCyclesAhead+currentCycle

def removeFromDaoistCycleTracker(update: Update, _: CallbackContext,dictKey):
    _.user_data[DAOISTCYCLETRACKER].pop(dictKey,None)
    logger.debug("removing {0} from daoist cycle tracker".format(dictKey))


def removeFromSatCycleTracker(update: Update, _: CallbackContext,dictKey):
    _.user_data[SATISFACTIONCYCLETRACKER].pop(dictKey,None)
    logger.debug("removing {0} from sat cycle tracker".format(dictKey))

def removeFromWarCycleTracker(update: Update, _: CallbackContext,dictKey):
    _.user_data[WARCYCLETRACKER].pop(dictKey,None)
    logger.debug("removing {0} from war cycle tracker".format(dictKey))

    
def notifyWarDeclaration(user_id:int,username:str, otherUserId:int):
    pgres.declareWarWith(user_id,username,otherUserId)


def removeWarDeclaration(user_id:int,username:str, otherUsername:str):
    pgres.removeDeclareWar(user_id,username,otherUsername)
