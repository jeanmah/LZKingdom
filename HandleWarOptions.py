BACKWAR, OPTION1, OPTION2, OPTION3, OPTION4, OPTION5, OPTION6, OPTION7, OPTION8, OPTION9, OPTION10 = range(11)

from telegram.ext import  Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import logging

import KingdomResources as KR
import indivKingdomLogic as indivK 
import HandleGameCyclesUpdates as gameCycles
import postgresqlCommands as pgres

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

STARTEDDIPLOMACY = "STARTEDDIPLOMACY"
ACCEPTDIPLOMACY = "ACCEPTDIPLOMACY"
AFTERMESSAGE = "AFTERMESSAGE"

def startDiplomacyOptions(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))

    currentAttackedBy = _.user_data["Being Attacked By"]
    currenlyInDiplomacyWith = _.user_data[STARTEDDIPLOMACY]

    keyboard = [[InlineKeyboardButton("Back to War Options", callback_data=str(BACKWAR))]]    
    for i in range(len(currentAttackedBy)):
        if(currentAttackedBy[i] not in currenlyInDiplomacyWith):
            keyboard.append([InlineKeyboardButton("{}".format(currentAttackedBy[i]), callback_data=str(i+1))])
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    currentDiplomacyMessage = "*\nStarted Diplomacy With*"
    if len(currenlyInDiplomacyWith) ==0:
        currentDiplomacyMessage +="\n~None~"
    else:
        for kingdom in currenlyInDiplomacyWith:
            currentDiplomacyMessage+=u'\n📜'
            currentDiplomacyMessage+=kingdom

    effectiveDisplayMessage = "*Start Diplomacy*\n{0}".format(currentDiplomacyMessage)

    query.edit_message_text(
        text=effectiveDisplayMessage, reply_markup=reply_markup,parse_mode= 'Markdown'
    )

    return int(query.data)


def acceptDiplomacyOptions(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))

    wantDiplomacyKingdoms = pgres.getWantOwnDiplomacy(query.from_user.id)
    print("want diplomacy ",query.from_user.id,wantDiplomacyKingdoms)
    _.user_data[ACCEPTDIPLOMACY] = wantDiplomacyKingdoms

    keyboard = [[InlineKeyboardButton("Back to War Options", callback_data=str(BACKWAR))]]    
    for i in range(len(wantDiplomacyKingdoms)):
        keyboard.append([InlineKeyboardButton("{}".format(wantDiplomacyKingdoms[i]), callback_data=str(i+1))])
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    acceptDiplomacyMessage = "*\nKingdoms that initiated diplomacy with you*"
    if len(wantDiplomacyKingdoms)==0:
        acceptDiplomacyMessage +="\n~None~"
    else:
        for kingdom in wantDiplomacyKingdoms:
            acceptDiplomacyMessage+=u'\n📜'
            acceptDiplomacyMessage+=kingdom

    effectiveDisplayMessage = "*Accept Diplomacy*\n{0}".format(acceptDiplomacyMessage)

    query.edit_message_text(
        text=effectiveDisplayMessage, reply_markup=reply_markup,parse_mode= 'Markdown'
    )

    return int(query.data)

def withdrawWarOptions(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))

    attacking = _.user_data["Declared War With"]

    keyboard = [[InlineKeyboardButton("Back to War Options", callback_data=str(BACKWAR))]]    
    
    for i in range(len(attacking)):
        keyboard.append([InlineKeyboardButton("{}".format(attacking[i]), callback_data=str(i+1))])
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    warMessage = "*Declared War With*"
    if(len(attacking)==0):
        warMessage+="\n~None~"
    else:
        for kingdom in attacking:
            warMessage+=u'\n⚔️'
            warMessage+=kingdom

    effectiveDisplayMessage = "*Withdraw from War*\n\n{0}".format(warMessage)

    query.edit_message_text(
        text=effectiveDisplayMessage, reply_markup=reply_markup,parse_mode= 'Markdown'
    )

    return int(query.data)

def handleStartDiplomacy(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))

    OldValues = {"Start Diplomacy With":_.user_data[STARTEDDIPLOMACY]}
    currentAttackedBy = _.user_data["Being Attacked By"]
    chosenKingdom = currentAttackedBy[int(query.data)-1]
    _.user_data[STARTEDDIPLOMACY].append(chosenKingdom)
    
    beforeList = pgres.getWantOtherDiplomacy(chosenKingdom)
    beforeList.append(query.from_user.username)
    pgres.updateOtherWantDiplomacy(beforeList, chosenKingdom)

    gameCycles.modifyDaoistCycleTracker(update,_,STARTEDDIPLOMACY,0,20)
    gameCycles.modifySatCycleTracker(update,_,STARTEDDIPLOMACY,0,20)
    
    NewValues = {"Start Diplomacy With":_.user_data[STARTEDDIPLOMACY]}
    return gameCycles.doNextRound(update,_, OldValues, NewValues)


def handleAcceptDiplomacy(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))

    wantDiplomacyKingdoms = _.user_data[ACCEPTDIPLOMACY]

    chosenKingdom = wantDiplomacyKingdoms[int(query.data)-1]

    #remove from declared war 
    declareWarList = _.user_data["Declared War With"]
    declareWarList.pop(declareWarList.index(chosenKingdom))
    _.user_data["Declared War With"] =declareWarList
    #remove from past declared war 
    neightbouringKingdomList =  _.user_data["Declare War on neighbouring kingdom"]
    neightbouringKingdomList.pop(neightbouringKingdomList.index(chosenKingdom))
    _.user_data["Declare War on neighbouring kingdom"] = neightbouringKingdomList

    beforeList = pgres.getOtherAcceptDiplomacy(chosenKingdom)
    beforeList.append(query.from_user.username)
    pgres.updateOtherAcceptDiplomacy(beforeList, chosenKingdom)

    beforeList = pgres.getWantOwnDiplomacy(query.from_user.id)
    beforeList.pop(beforeList.index(chosenKingdom))
    pgres.updateOwnWantDiplomacy(beforeList, query.from_user.id)

    gameCycles.modifyDaoistCycleTracker(update,_,ACCEPTDIPLOMACY,0,10)
    gameCycles.modifySatCycleTracker(update,_,ACCEPTDIPLOMACY,0,10)
    
    gameCycles.removeWarDeclaration(query.from_user.id,query.from_user.username,chosenKingdom)
    
    OldValues = {"Accept Diplomacy From":""}
    NewValues = {"Accept Diplomacy From":chosenKingdom}
    return gameCycles.doNextRound(update,_, OldValues, NewValues)


def handleWithdrawWar(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))

    attacking = _.user_data["Declared War With"]

    chosenKingdom = attacking[int(query.data)-1]
    print("chosen kingdom",chosenKingdom)

    #remove from declared war 

    attacking.pop(attacking.index(chosenKingdom))
    _.user_data["Declared War With"] = attacking
    #remove from past declared war 
    neighbouringKingdom = _.user_data["Declare War on neighbouring kingdom"]
    neighbouringKingdom.pop(neighbouringKingdom.index(chosenKingdom))
    _.user_data["Declare War on neighbouring kingdom"] = neighbouringKingdom

    if(chosenKingdom in KR.staticKingdomDict):
        gameCycles.removeFromWarCycleTracker(update,_,chosenKingdom)
    else:
        #withdraw from the other players being attacked by 
        beforeList = pgres.getOtherAttackedBy(chosenKingdom)
        beforeList.pop(beforeList.index(query.from_user.username))
        pgres.updateAttackedBy(beforeList, chosenKingdom)

    gameCycles.modifyDaoistCycleTracker(update,_,"WITHDRAWWAR",0,10)
    gameCycles.modifySatCycleTracker(update,_,"WITHDRAWWAR",0,10)
    
    OldValues = {"Withdraw From War With":""}
    NewValues = {"Withdraw From War With":chosenKingdom}
    return gameCycles.doNextRound(update,_, OldValues, NewValues)

def handleEndOfWar(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data)) 
    effectiveIndex = int(query.data)

    effectiveMessage = "*OUTCOME*"
    effectiveMessage+="\n\n{}".format(KR.EndOfWarMessages[effectiveIndex])

    if(effectiveIndex==0):
        gameCycles.modifyDaoistCycleTracker(update,_,"ENDOFWAR",0,-100)
        gameCycles.modifySatCycleTracker(update,_,"ENDOFWAR",0,5)
    elif(effectiveIndex==1):
        num_villagers = _.user_data["Num Villagers"]
        numToLeave = int(0.5*num_villagers)
        _.user_data["Num Villagers"] = num_villagers - numToLeave
        gameCycles.modifyDaoistCycleTracker(update,_,"ENDOFWAR",0,-200)
        gameCycles.modifySatCycleTracker(update,_,"ENDOFWAR",0,-50)
        effectiveMessage +="\n\nYou had {} villagers at first".format(num_villagers)
        effectiveMessage +="\n\n{0} villagers have left your kingdom".format(numToLeave)
        effectiveMessage +="\n\nYou have {} villagers left".format(num_villagers-numToLeave)
    else:
        gameCycles.modifyDaoistCycleTracker(update,_,"ENDOFWAR",0,100)
        gameCycles.modifySatCycleTracker(update,_,"ENDOFWAR",0,50)

    keyboard = [[InlineKeyboardButton("Continue", callback_data=str(AFTERMESSAGE))]]    

    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        text=effectiveMessage, reply_markup=reply_markup,parse_mode= 'Markdown'
    )

    return indivK.ENDOFWAREVENT

def handleAfterMessage(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    return gameCycles.doNextRound(update,_, {}, {})

