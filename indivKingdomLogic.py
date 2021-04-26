from telegram.ext import  Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import logging
import copy
import KingdomResources as KR
import HandleInfrActOptions as InfraActOpt
import HandleOtherActOptions as OtherActOpt
import HandleGameCyclesUpdates as gameCycles
import HandleWarOptions as WarOpt
import HandleRandomEvents as RandOpts
import RandomEventsCreation as RandEvent

import postgresqlCommands as pgres
import copy

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


#STATES
#gen, infra actions, other actions, war actions, random events, cycleUpdate
HOME, STATS, INFRASTRUCTURE, OTHERACTIONS, WAR , HELP , ENDGAME, BACKHOME, \
INCMILSPENDING, BUILDFARM, BUILDFISH, BEAUTIFYPALACE, HIGHERSCH, ESTAPPR, MUSICSCH, BUILDIRON , \
PROMOVALS, DECLAREWAR, OCCUPYUNCLAIMED, INCTAXES, IMPLTAXSERVICES, DONOTHING, \
STARTDIPLOMACY, ACCEPTDIPLOMACY, WITHDRAW, \
RANDOMEVENTS, CYCLEUPDATE, ENDOFWAREVENT = range(len(KR.InfraActionsDict)+len(KR.OtherActionsDict)+ 8 +3 +3) 

infraActionsStates = [INCMILSPENDING, BUILDFARM, BUILDFISH, BEAUTIFYPALACE, HIGHERSCH, ESTAPPR, MUSICSCH, BUILDIRON]
otherActionsStates = [PROMOVALS, DECLAREWAR, OCCUPYUNCLAIMED, INCTAXES, IMPLTAXSERVICES, DONOTHING]

def startKingdom(update: Update, _: CallbackContext) -> int:

    """Send message on `/start`."""
    # Get user that sent /start and log his name
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    logger.info("chat id %d",update.message.chat_id)
    #_.user_data[PLAYERS] = []
    if(update.message.chat.type != "private"):
        _.bot.sendMessage(chat_id = update.message.chat_id,text= "this command is only used in private chats")
        return ConversationHandler.END
    if(not pgres.checkUserExists(user.id)):
        _.bot.sendMessage(chat_id = update.message.chat_id,text= "please join a game from a group chat")
        return ConversationHandler.END
    if not pgres.getStartedGame(user.id):
        _.bot.sendMessage(chat_id = update.message.chat_id,text= "game has not started")
        return ConversationHandler.END

    createUserVariables(user.id,_)

    home_keyboard = [ 
        [
            InlineKeyboardButton("Build Infrastructure", callback_data=str(INFRASTRUCTURE)),
            InlineKeyboardButton("Other Actions", callback_data=str(OTHERACTIONS)),
        ],
        [
            InlineKeyboardButton("War Room", callback_data=str(WAR)),
            InlineKeyboardButton("Help", callback_data=str(HELP)),
        ],
        [
             InlineKeyboardButton("End Game", callback_data=str(ENDGAME)),
        ]
      ]
    reply_markup = InlineKeyboardMarkup(home_keyboard)

    startMessage = '''*WELCOME*
    \nYour fellow villagers have decided that you should be their ruler. 
    \nCreate the best living envrionment you can for them. 
    \nYou may expand your village, build infrastructures and create rules. 
    \nEvery now and a then, your villagers might come to you for something. 
    \nDo what is best. Good luck :)
    '''

    _.bot.sendMessage(chat_id = update.message.chat_id,text= startMessage, parse_mode= 'Markdown')

    #send game keys
    _.bot.sendMessage(chat_id = update.message.chat_id,text= "{0}\n\n{1}".format(getStatsMessage(_),getInfraMessage(_)),reply_markup=reply_markup,timeout =1800 , parse_mode= 'Markdown')
    
    return HOME

def backHome(update: Update, _: CallbackContext) -> int:

    query = update.callback_query
    query.answer()
    
    home_keyboard = [ 
        [
            InlineKeyboardButton("Build Infrastructure", callback_data=str(INFRASTRUCTURE)),
            InlineKeyboardButton("Other Actions", callback_data=str(OTHERACTIONS)),
        ],
        [
            InlineKeyboardButton("War Room", callback_data=str(WAR)),
            InlineKeyboardButton("Help", callback_data=str(HELP)),
        ],
        [
             InlineKeyboardButton("End Game", callback_data=str(ENDGAME)),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(home_keyboard)
    query.edit_message_text(
        text="{0}\n\n{1}".format(getStatsMessage(_),getInfraMessage(_)), reply_markup=reply_markup,parse_mode= 'Markdown'
    )

    return HOME    

def createCycleVariables(user_id:int, callBackContext: CallbackContext):
    callBackContext.user_data[gameCycles.CURRENTCYCLE] = 0
    callBackContext.user_data[gameCycles.DAOISTCYCLETRACKER] = {}
    callBackContext.user_data[gameCycles.SATISFACTIONCYCLETRACKER] = {}
    callBackContext.user_data[gameCycles.WARCYCLETRACKER] = {}

def createStatsVariables(user_id:int, callBackContext: CallbackContext):
    for statvar in KR.statsDict.values():
        if(isinstance(statvar.initVal,list) or isinstance(statvar.initVal,dict)):
            callBackContext.user_data[statvar.statName] = copy.deepcopy(statvar.initVal)
        else:
            callBackContext.user_data[statvar.statName] = statvar.initVal
    pgres.updateDaoistSatScore(user_id,KR.statsDict["DaoistPoints"].initVal,KR.statsDict["PeopleSatisfaction"].initVal)

def createInfraVariables(user_id:int, callBackContext: CallbackContext):
    for infrVar in KR.infraDict.values():
        if(isinstance(infrVar.initVal,list) or isinstance(infrVar.initVal,dict)):
            callBackContext.user_data[infrVar.infraName] = copy.deepcopy(infrVar.initVal)
        else:
            callBackContext.user_data[infrVar.infraName] = infrVar.initVal

def createInfraActionVariables(user_id:int, callBackContext: CallbackContext):
    for infrActKeys in KR.InfraActionsDict.keys():
        option = KR.InfraActionsDict[infrActKeys].defaultOption
        if(isinstance(option,list) or isinstance(option,dict)):
            callBackContext.user_data[infrActKeys] = copy.deepcopy(option)
        else:
            callBackContext.user_data[infrActKeys] = option
    callBackContext.user_data["Beautify Palace"] = callBackContext.user_data['Beauty']

def createOtherActionVariables(user_id:int, callBackContext: CallbackContext):
    for otherActKeys in KR.OtherActionsDict.keys():
        option = KR.OtherActionsDict[otherActKeys].defaultOption
        if(isinstance(option,list) or isinstance(option,dict)):
            callBackContext.user_data[otherActKeys] = copy.deepcopy(option)
        else:
            callBackContext.user_data[otherActKeys] =option

def createWarActionVariables(user_id:int, callBackContext: CallbackContext):
    callBackContext.user_data[WarOpt.STARTEDDIPLOMACY] = []
    callBackContext.user_data[WarOpt.ACCEPTDIPLOMACY] = []

def createRandomActionVariables(user_id:int, callBackContext: CallbackContext):
    callBackContext.user_data[RandOpts.AVAILABLEEVENTS] = list(range(len(RandEvent.randomEventList)))
    callBackContext.user_data[RandOpts.CURRENTEVENT] = -1
    callBackContext.user_data[RandOpts.NUMJUDGINGDONE] = 0

def createUserVariables(user_id:int, callBackContext: CallbackContext):
    createCycleVariables(user_id, callBackContext)
    createStatsVariables(user_id, callBackContext)
    createInfraVariables(user_id, callBackContext)
    createInfraActionVariables(user_id, callBackContext)
    createOtherActionVariables(user_id, callBackContext)
    createWarActionVariables(user_id, callBackContext)
    createRandomActionVariables(user_id, callBackContext)


def removeGameVariables(user_id:int, callBackContext: CallbackContext):
    for statvar in KR.statsDict.values():
        callBackContext.user_data.pop(statvar.statName,None)

    for infrVar in KR.infraDict.values():
        callBackContext.user_data.pop(infrVar.infraName,None)

    for infrActKeys in KR.InfraActionsDict.keys():
        callBackContext.user_data.pop(infrActKeys,None)
    
    for otherActKeys in KR.OtherActionsDict.keys():
        callBackContext.user_data.pop(otherActKeys,None)

    callBackContext.user_data.pop(gameCycles.CURRENTCYCLE,None)
    callBackContext.user_data.pop(gameCycles.DAOISTCYCLETRACKER,None)
    callBackContext.user_data.pop(gameCycles.SATISFACTIONCYCLETRACKER,None)
    callBackContext.user_data.pop(gameCycles.WARCYCLETRACKER,None)

    callBackContext.user_data.pop(WarOpt.STARTEDDIPLOMACY,None)
    callBackContext.user_data.pop(WarOpt.ACCEPTDIPLOMACY,None)

    callBackContext.user_data.pop(RandOpts.AVAILABLEEVENTS,None)
    callBackContext.user_data.pop(RandOpts.CURRENTEVENT,None)
    callBackContext.user_data.pop(RandOpts.NUMJUDGINGDONE,None)


def getStatsMessage(callBackContext: CallbackContext) -> str:
    statMessage = "*Your Kingdom Status*\n" 
    for statvar in KR.statsDict.values():
        statMessage+=u'\n✔️ '
        statMessage+=str(statvar.statName) + " : "
        statVal = callBackContext.user_data[statvar.statName]

        if isinstance(statVal, list):
            statMessage+="{}".format(', '.join(statVal))
            if(len(statVal) ==0 ):
                statMessage+="~None~"
        elif isinstance(statVal, bool):
            possibilities = statvar.units.split("/")
            if(statVal):
                statMessage+= possibilities[0]
            else:
                statMessage+= possibilities[1]
        else:
            statMessage+=str(statVal)

        if(statvar.category):
            maxCatVals = statvar.categoryMax
            currentCatgory = None
            for c in maxCatVals:
                if(statVal<maxCatVals[c]):
                    currentCatgory = c
                    break
            if(currentCatgory is None):
                currentCatgory = list(maxCatVals)[-1]
            statMessage+="/{0} {1}".format(maxCatVals[currentCatgory],currentCatgory)
        else:
            if not isinstance(statVal, bool):
                statMessage+=" "
                statMessage+=str(statvar.units)
    return statMessage


def infrastructure(update: Update, _: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    
    keyboard = [[InlineKeyboardButton("Back to Home", callback_data=str(BACKHOME))]]
    for i in range(0,len(KR.InfraActionsDict)):
        keyboard.append([InlineKeyboardButton(list(KR.InfraActionsDict)[i], callback_data=str(infraActionsStates[i]))])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=getInfraMessage(_), reply_markup=reply_markup, parse_mode= 'Markdown'
    )
    return INFRASTRUCTURE

def handleBuildInfra(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))
    effectiveIndex = infraActionsStates.index(int(query.data))
    dicKey = list(KR.InfraActionsDict)[effectiveIndex]
    actionClassInstance = KR.InfraActionsDict[dicKey]
    current_chosen_option = _.user_data[list(KR.InfraActionsDict)[effectiveIndex]]

    keyboard = [[InlineKeyboardButton("Back to Infrastructure Options", callback_data=str(InfraActOpt.BACKINFRA))]]
    for i in range(len(actionClassInstance.options)):
        if(current_chosen_option != actionClassInstance.options[i]):
            keyboard.append([InlineKeyboardButton(actionClassInstance.options[i], callback_data=str(i+1))])
    reply_markup = InlineKeyboardMarkup(keyboard)

    effective_message = "*Infrastructure Actions*\n\n{0}".format(actionClassInstance.displayMessage)
    for preq in actionClassInstance.pre_req:
        effective_message +="\n\n{0}".format(preq)
    if(dicKey == "Beautify Palace"):
        effective_message+="\n\nThe current beauty level is {0}".format(current_chosen_option)
    else:
        effective_message+="\n\nThe current chosen option is {0}".format(current_chosen_option)

    query.edit_message_text( text=effective_message, reply_markup=reply_markup,parse_mode= 'Markdown')
    return int(query.data)

def getInfraMessage(callBackContext: CallbackContext) -> str:
    infraMessage = "*Your Kingdom Infrastructure*\n"
    for infraVar in KR.infraDict.values():
        infraMessage+=u'\n✔️ '
        infraMessage+="{0} : ".format(infraVar.infraName)
        infraVal = callBackContext.user_data[infraVar.infraName]
        if isinstance(infraVal, list):
            infraMessage+="{}".format(', '.join(infraVal))
        elif isinstance(infraVal, bool):
            possibilities = infraVar.units.split("/")
            if(infraVal):
                infraMessage+= possibilities[0]
            else:
                infraMessage+= possibilities[1]
        else:
            infraMessage+=str(infraVal)
        if(infraVar.category):
            maxCatVals = infraVar.categoryMax
            currentCatgory = None
            for c in maxCatVals:
                if(infraVal<maxCatVals[c]):
                    currentCatgory = c
                    break
            if(currentCatgory is None):
                currentCatgory = list(maxCatVals)[-1]
            infraMessage+="/{0} {1}".format(maxCatVals[currentCatgory],currentCatgory)
        else:
            if not isinstance(infraVal, bool):
                print("units",infraVar.units,infraVal)
                infraMessage+=" "
                infraMessage+=str(infraVar.units)
        
    return infraMessage


def otherActions(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    
    keyboard = [[InlineKeyboardButton("Back to Home", callback_data=str(BACKHOME))]]
    for i in range(0,len(KR.OtherActionsDict)):
        keyboard.append([InlineKeyboardButton(list(KR.OtherActionsDict)[i], callback_data=str(otherActionsStates[i]))])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="*Do these actions to change your Kingdom's status*\n\n{0}".format(getStatsMessage(_)), reply_markup=reply_markup,parse_mode= 'Markdown'
    )
    return OTHERACTIONS

def warActions(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Back to Home", callback_data=str(BACKHOME))],
        [
            InlineKeyboardButton("Initiate Diplomacy", callback_data=str(STARTDIPLOMACY)), 
            InlineKeyboardButton("Accept Diplomacy", callback_data=str(ACCEPTDIPLOMACY))
        ],
        [InlineKeyboardButton("Withdraw from War", callback_data=str(WITHDRAW))],
    ]  

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="*War Room*\n\n{0}".format(getWarMessage(_)), reply_markup=reply_markup,parse_mode= 'Markdown'
    )

    return WAR

    # TODO: war actions diplomacy, accept diplomacy, withdraw if attacking
def getWarMessage( callBackContext: CallbackContext) ->str:
    warMessage = "*Your War Status*\n"     
    
    warDeclarations = KR.statsDict["declaredWarWith"]
    warMessage+="\n*{0}*".format(warDeclarations.statName)
    currentWarDec = callBackContext.user_data["Declared War With"]
    if(len(currentWarDec)==0):
        warMessage+="\n~None~"
    else:
        for kingdom in currentWarDec:
            warMessage+=u'\n⚔️'
            warMessage+=kingdom

    attackedByStats = KR.statsDict["beingAttackedBy"]
    warMessage+="\n\n*{0}*".format(attackedByStats.statName)
    currentAttackedBy = callBackContext.user_data["Being Attacked By"]
    if(len(currentAttackedBy)==0):
        warMessage+="\n~None~"
    else:
        for kingdom in currentAttackedBy:
            warMessage+=u'\n🛡'
            warMessage+=kingdom
    return warMessage

def helpDialog(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    
    keyboard = [[InlineKeyboardButton("Back to Home", callback_data=str(BACKHOME))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=KR.instructionsMessage, reply_markup=reply_markup,parse_mode= 'Markdown'
    )
    return HELP


def endGameDialog(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Back to Home", callback_data=str(BACKHOME))],
        [InlineKeyboardButton("ENDGAME", callback_data=str(ENDGAME))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    endMessage = "*End Game*\n\n Are you sure you want to end this game?\n\n"
    endMessage+=u'⚠️WARNING: Ending the game will end the game for all users in the group chat'
    query.edit_message_text(
        text=endMessage, reply_markup=reply_markup,parse_mode= 'Markdown'
    )
    return ENDGAME

def end(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    endMessage = u'🏰*Game Ended*'
    endMessage+="\n\nThese are your final stats\n"
    endMessage += "{0}\n\n{1}".format(getStatsMessage(_),getInfraMessage(_))
    endMessage+="\nHead back to the group chat to see who won"

    query.edit_message_text(text=endMessage, parse_mode= 'Markdown')
    gameCycles.endGame(update,_,query.from_user.id)
    _.bot.sendMessage(chat_id = pgres.getGroupIdOfPlayer(update.effective_message.chat_id),text="The game has ended, please send /get_rankings to get the rankings")

    return ConversationHandler.END



def getIndivConversationHandler() ->ConversationHandler:
    conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start_kingdom', startKingdom)],
            states={
                HOME: [
                    CallbackQueryHandler(infrastructure, pattern='^' + str(INFRASTRUCTURE) + '$'),
                    CallbackQueryHandler(otherActions, pattern='^' + str(OTHERACTIONS) + '$'),
                    CallbackQueryHandler(warActions, pattern='^' + str(WAR) + '$'),
                    CallbackQueryHandler(helpDialog, pattern='^' + str(HELP) + '$'),
                    CallbackQueryHandler(endGameDialog, pattern='^' + str(ENDGAME) + '$'),
                ],
                INFRASTRUCTURE:[
                    CallbackQueryHandler(backHome, pattern='^' + str(BACKHOME) + '$'),
                    CallbackQueryHandler(handleBuildInfra),
                ], 
                OTHERACTIONS:[
                    CallbackQueryHandler(backHome, pattern='^' + str(BACKHOME) + '$'),
                    CallbackQueryHandler(OtherActOpt.valuesOptions, pattern='^' + str(PROMOVALS) + '$'),
                    CallbackQueryHandler(OtherActOpt.declareWarOptions, pattern='^' + str(DECLAREWAR) + '$'),
                    CallbackQueryHandler(OtherActOpt.occupyUnclaimedLandOptions, pattern='^' + str(OCCUPYUNCLAIMED) + '$'),
                    CallbackQueryHandler(OtherActOpt.incTaxesOptions, pattern='^' + str(INCTAXES) + '$'),
                    CallbackQueryHandler(OtherActOpt.inmplementTaxServiceOptions, pattern='^' + str(IMPLTAXSERVICES) + '$'),
                    CallbackQueryHandler(OtherActOpt.doNothingOptions, pattern='^' + str(DONOTHING) + '$'),
                ], 
                WAR:[
                    CallbackQueryHandler(backHome, pattern='^' + str(BACKHOME) + '$'),
                    CallbackQueryHandler(WarOpt.startDiplomacyOptions, pattern='^' + str(STARTDIPLOMACY) + '$'),
                    CallbackQueryHandler(WarOpt.acceptDiplomacyOptions, pattern='^' + str(ACCEPTDIPLOMACY) + '$'),
                    CallbackQueryHandler(WarOpt.withdrawWarOptions, pattern='^' + str(WITHDRAW) + '$'),
                ],
                HELP:[
                    CallbackQueryHandler(backHome, pattern='^' + str(BACKHOME) + '$'),
                ],
                ENDGAME:[
                    CallbackQueryHandler(backHome, pattern='^' + str(BACKHOME) + '$'),
                    CallbackQueryHandler(end, pattern='^' + str(ENDGAME) + '$'),
                ],
                INCMILSPENDING:[
                    CallbackQueryHandler(infrastructure, pattern='^' + str(InfraActOpt.BACKINFRA) + '$'),
                    CallbackQueryHandler(InfraActOpt.handleIncMilSpending),
                ], 
                BUILDFARM:[
                    CallbackQueryHandler(infrastructure, pattern='^' + str(InfraActOpt.BACKINFRA) + '$'),
                    CallbackQueryHandler(InfraActOpt.handleBuildFarm),
                ], 
                BUILDFISH:[
                    CallbackQueryHandler(infrastructure, pattern='^' + str(InfraActOpt.BACKINFRA) + '$'),
                    CallbackQueryHandler(InfraActOpt.handleBuildFish),
                ], 
                BEAUTIFYPALACE:[
                    CallbackQueryHandler(infrastructure, pattern='^' + str(InfraActOpt.BACKINFRA) + '$'),
                    CallbackQueryHandler(InfraActOpt.handlebeautifyPalace),
                ], 
                HIGHERSCH:[
                    CallbackQueryHandler(infrastructure, pattern='^' + str(InfraActOpt.BACKINFRA) + '$'),
                    CallbackQueryHandler(InfraActOpt.handleBuildHigherSchool),
                ], 
                ESTAPPR:[
                    CallbackQueryHandler(infrastructure, pattern='^' + str(InfraActOpt.BACKINFRA) + '$'),
                    CallbackQueryHandler(InfraActOpt.handleEstablishApprentiships),
                ], 
                MUSICSCH:[
                    CallbackQueryHandler(infrastructure, pattern='^' + str(InfraActOpt.BACKINFRA) + '$'),
                    CallbackQueryHandler(InfraActOpt.handleBuildMusic),
                ], 
                BUILDIRON :[
                    CallbackQueryHandler(infrastructure, pattern='^' + str(InfraActOpt.BACKINFRA) + '$'),
                    CallbackQueryHandler(InfraActOpt.handleBuildIron),
                ],

                #other actions
                PROMOVALS:[
                    CallbackQueryHandler(otherActions, pattern='^' + str(OtherActOpt.BACKOTHERACTIONS) + '$'),
                    CallbackQueryHandler(OtherActOpt.handlePromoVals),
                ], 
                DECLAREWAR:[
                    CallbackQueryHandler(otherActions, pattern='^' + str(OtherActOpt.BACKOTHERACTIONS) + '$'),
                    CallbackQueryHandler(OtherActOpt.handleDeclareWar),
                ], 
                OCCUPYUNCLAIMED:[
                    CallbackQueryHandler(otherActions, pattern='^' + str(OtherActOpt.BACKOTHERACTIONS) + '$'),
                    CallbackQueryHandler(OtherActOpt.handleOccupyUnclaimed),
                ], 
                INCTAXES:[
                    CallbackQueryHandler(otherActions, pattern='^' + str(OtherActOpt.BACKOTHERACTIONS) + '$'),
                    CallbackQueryHandler(OtherActOpt.handleIncTaxes),
                ], 
                IMPLTAXSERVICES:[
                    CallbackQueryHandler(otherActions, pattern='^' + str(OtherActOpt.BACKOTHERACTIONS) + '$'),
                    CallbackQueryHandler(OtherActOpt.handleImplementTaxServices),
                ], 
                DONOTHING: [
                    CallbackQueryHandler(otherActions, pattern='^' + str(OtherActOpt.BACKOTHERACTIONS) + '$'),
                    CallbackQueryHandler(OtherActOpt.handleDoNothing),
                ],

                #war actions
                STARTDIPLOMACY:[
                    CallbackQueryHandler(warActions, pattern='^' + str(WarOpt.BACKWAR) + '$'),
                    CallbackQueryHandler(WarOpt.handleStartDiplomacy),
                ],
                ACCEPTDIPLOMACY:[
                    CallbackQueryHandler(warActions, pattern='^' + str(WarOpt.BACKWAR) + '$'),
                    CallbackQueryHandler(WarOpt.handleAcceptDiplomacy),
                ],
                WITHDRAW:[
                    CallbackQueryHandler(warActions, pattern='^' + str(WarOpt.BACKWAR) + '$'),
                    CallbackQueryHandler(WarOpt.handleWithdrawWar),
                ],

                #Random events
                RANDOMEVENTS:[
                    CallbackQueryHandler(RandOpts.handleEventCompleted,pattern='^' + str(RandOpts.EVENTCOMPLETED) + '$'),
                    CallbackQueryHandler(RandOpts.handleRandomEvents),
                ],

                #cycle update
                CYCLEUPDATE:[
                    CallbackQueryHandler(backHome, pattern='^' + str(BACKHOME) + '$'),
                ],

                #ENDOFWAREVENT
                ENDOFWAREVENT:[
                    CallbackQueryHandler(WarOpt.handleAfterMessage, pattern='^' + str(WarOpt.AFTERMESSAGE) + '$'),
                    CallbackQueryHandler(WarOpt.handleEndOfWar),
                ],

            },
            fallbacks=[CommandHandler('start_kingdom', startKingdom)],
        )
    return conv_handler