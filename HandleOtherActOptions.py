BACKOTHERACTIONS, OPTION1, OPTION2, OPTION3, OPTION4, OPTION5, OPTION6, OPTION7, OPTION8, OPTION9, OPTION10 = range(11)

from telegram.ext import  Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import logging
import copy

import KingdomResources as KR
import indivKingdomLogic as indivK
import postgresqlCommands as pgres
import HandleGameCyclesUpdates as gameCycles
import HandleInfrActOptions as InfraActOpt

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

DECLARINGWAROPTIONS = "DECLARINGWAROPTIONS" 


def valuesOptions(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))
    effectiveIndex = indivK.otherActionsStates.index(int(query.data))
    dicKey = list(KR.OtherActionsDict)[effectiveIndex]
    actionClassInstance = KR.OtherActionsDict[dicKey]
    currentlyPromotedVals = _.user_data["Values Promoted"]

    
    keyboard = [[InlineKeyboardButton("Back to Other Action Options", callback_data=str(BACKOTHERACTIONS))]]    
    for i in range(len(actionClassInstance.options)):
        if(actionClassInstance.options[i] not in currentlyPromotedVals):
            keyboard.append([InlineKeyboardButton("Promote {}".format(actionClassInstance.options[i]), callback_data=str(i+1))])
        else:
            keyboard.append([InlineKeyboardButton("Stop promoting {}".format(actionClassInstance.options[i]), callback_data=str(i+1))])
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    effectiveDisplayMessage = "*Promote Values*\n\n{0}".format(actionClassInstance.displayMessage)
    if(len(currentlyPromotedVals)>0):
        effectiveDisplayMessage +="You are currently promoting these values"
    for i in range(len(currentlyPromotedVals)):
        effectiveDisplayMessage+="\n{0}. {1}".format(i+1,currentlyPromotedVals[i])

    query.edit_message_text(
        text=effectiveDisplayMessage, reply_markup=reply_markup,parse_mode= 'Markdown'
    )

    return int(query.data)

def declareWarOptions(update: Update, _: CallbackContext) -> int:
    return getDeclareWarMessage(update,_)


def occupyUnclaimedLandOptions(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))
    effectiveIndex = indivK.otherActionsStates.index(int(query.data))
    dicKey = list(KR.OtherActionsDict)[effectiveIndex]
    actionClassInstance = KR.OtherActionsDict[dicKey] #put the names here 
    occupiedLand = _.user_data["Occupy unclaimed land"]
    
    effectiveDisplayMessage = "*Unclaimed Land*\n\n{0}".format(actionClassInstance.displayMessage)
    if(len(occupiedLand)>0):
        effectiveDisplayMessage +="\n\nYou have claimed these lands"
    for i in range(len(occupiedLand)):
        effectiveDisplayMessage+="\n{0}. {1}".format(i+1,occupiedLand[i])

    effectiveDisplayMessage +="\n\n*Options*"

    keyboard = [[InlineKeyboardButton("Back to Other Action Options", callback_data=str(BACKOTHERACTIONS))]]    
    
    count = 1
    found =False
    for landOptionNames in actionClassInstance.options:
        if(landOptionNames not in occupiedLand):
            landOptionsVals = actionClassInstance.options[landOptionNames]
            effectiveDisplayMessage +="\n*{0}* \nLand area {1} \nNum People {2}\n".format(landOptionNames, landOptionsVals.landArea, landOptionsVals.numPeople)
            keyboard.append([InlineKeyboardButton("{0}".format(landOptionNames), callback_data=str(count))])
            found = True
        count+=1
    if(not found):
        effectiveDisplayMessage += "\n~NONE~"
    reply_markup = InlineKeyboardMarkup(keyboard)  

    

    query.edit_message_text(
        text=effectiveDisplayMessage, reply_markup=reply_markup, parse_mode= 'Markdown'
    )
    return int(query.data)

def incTaxesOptions(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))
    effectiveIndex = indivK.otherActionsStates.index(int(query.data))
    dicKey = list(KR.OtherActionsDict)[effectiveIndex]
    actionClassInstance = KR.OtherActionsDict[dicKey]
    currentTaxes = _.user_data["Tax Amount"]

    keyboard = [[        
        InlineKeyboardButton("Back to Other Action Options", callback_data=str(BACKOTHERACTIONS)),
    ]]    
    for i in range(len(actionClassInstance.options)):
        keyboard.append([InlineKeyboardButton(actionClassInstance.options[i], callback_data=str(i+1))])
    reply_markup = InlineKeyboardMarkup(keyboard)  

    query.edit_message_text(
        text="*Taxes*\n\n{0}\nThe current tax amount is {1}".format(actionClassInstance.displayMessage,currentTaxes), reply_markup=reply_markup, parse_mode= 'Markdown'
    )
    return indivK.INCTAXES


def inmplementTaxServiceOptions(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))
    effectiveIndex = indivK.otherActionsStates.index(int(query.data))
    dicKey = list(KR.OtherActionsDict)[effectiveIndex]
    actionClassInstance = KR.OtherActionsDict[dicKey]
    current_chosen_option = _.user_data[list(KR.OtherActionsDict)[effectiveIndex]]

    keyboard = [[        
        InlineKeyboardButton("Back to Other Action Options", callback_data=str(BACKOTHERACTIONS)),
    ]]
    for i in range(len(actionClassInstance.options)):
        if(current_chosen_option != actionClassInstance.options[i]):
            keyboard.append([InlineKeyboardButton(actionClassInstance.options[i], callback_data=str(i+1))])
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        text="*Tax Services*\n\n{0}\nThe chosen option is {1}".format(actionClassInstance.displayMessage,current_chosen_option), reply_markup=reply_markup, parse_mode= 'Markdown'
    )
    return indivK.IMPLTAXSERVICES

def doNothingOptions(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    #logger.info("callback query data {}".format(query.data))
    effectiveIndex = indivK.otherActionsStates.index(int(query.data))
    dicKey = list(KR.OtherActionsDict)[effectiveIndex]
    actionClassInstance = KR.OtherActionsDict[dicKey]

    keyboard = [
        [ InlineKeyboardButton("Back to Other Action Options", callback_data=str(BACKOTHERACTIONS)) ],
        [ InlineKeyboardButton(actionClassInstance.options[0], callback_data=str(1))]
    ]
   
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        text="*Do Nothing*\n\n{0}".format(actionClassInstance.displayMessage), reply_markup=reply_markup,parse_mode= 'Markdown'
    )
    return indivK.DONOTHING


def handlePromoVals(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))
    otherActionInstance= KR.OtherActionsDict["Values Promoted"]
    valChosen = otherActionInstance.options[int(query.data)-1]
    print("val chosen",valChosen)
    already_chosen_values = _.user_data["Values Promoted"]
    print("promoted values",already_chosen_values)
    print("type",type(already_chosen_values))

    OldValues = {"Values Promoted":already_chosen_values}

    if valChosen in already_chosen_values:
        already_chosen_values.pop(already_chosen_values.index(valChosen))
        gameCycles.removeFromSatCycleTracker(update, _, valChosen)
        gameCycles.modifyDaoistCycleTracker(update, _, valChosen,0, 15)
    else:
        already_chosen_values.append(valChosen)
        gameCycles.modifySatCycleTracker(update, _,valChosen, 3, 15)
        gameCycles.modifyDaoistCycleTracker(update, _, valChosen, 0, -25)

    
    _.user_data["Values Promoted"] = already_chosen_values

    NewValues = {"Values Promoted":already_chosen_values}

    return gameCycles.doNextRound(update,_, OldValues, NewValues)

def handleDeclareWar(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))
    
    pastPresWarringKingdoms = _.user_data["Declare War on neighbouring kingdom"]
    
    military = _.user_data["Military Power"]

    if(military<500):
        return getDeclareWarMessage(update,_,"\nYou do not have at least 500 military points")

    valChosen = _.user_data[DECLARINGWAROPTIONS][int(query.data)-1]
    
    #update past wars 
    pastPresWarringKingdoms.append(valChosen[0])
    _.user_data["Declare War on neighbouring kingdom"] = pastPresWarringKingdoms
    
    if(valChosen[2]):
        gameCycles.modifyWarCycleTracker(update, _, valChosen[0], 5)
    if(len(pastPresWarringKingdoms))>2:
        gameCycles.modifyDaoistCycleTracker(update, _, "WAR", 0, -50)
    else:
        gameCycles.modifySatCycleTracker(update, _, "WAR", 2, 20)
    
    #update currently declared wars 
    currently_declared = copy.deepcopy(_.user_data["Declared War With"])
    print(currently_declared)
    OldValues = {"Declared War On":currently_declared}

    currently_declared.append(valChosen[0])
    _.user_data["Declared War With"] = currently_declared

    #check if val_chosen is another player 
    NewValues = {"Declared War On":currently_declared}

    if(not valChosen[2]):
        try:
            print("update.callback_query.from_user.id, username",update.callback_query.from_user.id,update.callback_query.from_user.username)
            gameCycles.notifyWarDeclaration(update.callback_query.from_user.id,update.callback_query.from_user.username,valChosen[1])
        except:
            return gameCycles.doNextRound(update,_, OldValues, NewValues)
    # "Declare War on neighbouring kingdom" :ActionClass(staticKingdomDict, ["You need a military score of at least 500 to declare war on someone", "You cannot declare war on someone who declare war on you first"], [],[],"Declare war on your friends and other kingdoms.\n If you win, their villagers and their land will belong to you"),


    return gameCycles.doNextRound(update,_, OldValues, NewValues)

def handleOccupyUnclaimed(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))
    otherActionInstance= KR.OtherActionsDict["Occupy unclaimed land"]
    staticResourceChosenKey = list(otherActionInstance.options)[int(query.data)-1]

    already_chosen_values = _.user_data["Occupy unclaimed land"]
    OldValues = {"Occupied Unclaimed Land": already_chosen_values}

    already_chosen_values.append(staticResourceChosenKey)
    _.user_data["Occupy unclaimed land"] = already_chosen_values

    _.user_data["Num Villagers"] += otherActionInstance.options[staticResourceChosenKey].numPeople
    _.user_data["Amt Of Land"] += otherActionInstance.options[staticResourceChosenKey].landArea
    
    if(len(already_chosen_values)>2):
        gameCycles.modifyDaoistCycleTracker(update, _, "UNOCCUPIED", 0, -10)
    else:
        gameCycles.modifyDaoistCycleTracker(update, _, "UNOCCUPIED", 0, 2)
        gameCycles.modifySatCycleTracker(update, _, "UNOCCUPIED", 0, 20)

    NewValues = {"Occupied Unclaimed Land": already_chosen_values}

    score, FarmOldValues, FarmNewValues = InfraActOpt.updateFarmScore(update,_)
    score, IronOldValues, IronNewValues = InfraActOpt.updateIronScore(update,_)

    OldValues.update(FarmOldValues)
    OldValues.update(IronOldValues)
    NewValues.update(FarmNewValues)
    NewValues.update(IronNewValues)

    return gameCycles.doNextRound(update,_,OldValues,NewValues)

def handleIncTaxes(update: Update, _: CallbackContext):
    
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))
    otherActionInstance= KR.OtherActionsDict["Increase taxes"]
    valChosen = otherActionInstance.options[int(query.data)-1]
    currentTaxes = _.user_data["Tax Amount"]

    OldValues = {"Tax Amount": currentTaxes}

    if int(query.data)==1:
        currentTaxes +=10
    else:
        currentTaxes-=10
        currentTaxes = max(0,currentTaxes)
    
    if(currentTaxes<50):
        gameCycles.modifyDaoistCycleTracker(update, _, "TAXES", 0, 2)
        gameCycles.modifySatCycleTracker(update, _, "TAXES", 0, 5)
    else:
        gameCycles.modifyDaoistCycleTracker(update, _, "TAXES", 0, -3)
        gameCycles.modifySatCycleTracker(update, _, "TAXES", 0, -5)

    _.user_data["Tax Amount"] = currentTaxes
    InfraActOpt.updateMilitaryScore(update,_)

    NewValues = {"Tax Amount": currentTaxes}

    score, milOldValues, milNewValues = InfraActOpt.updateMilitaryScore(update,_)

    OldValues.update(milOldValues)
    NewValues.update(milNewValues)

    return gameCycles.doNextRound(update,_,OldValues,NewValues)


def handleImplementTaxServices(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))
    otherActionInstance= KR.OtherActionsDict["Implement tax services"]

    is_implementing = int(query.data) ==1
    _.user_data["Tax Services"] = is_implementing
    _.user_data["Implement tax services"] = otherActionInstance.options[int(query.data)-1]

    if(is_implementing):
        oldValues = {"Tax Services":"Not Implemented"}
        newValues = {"Tax Services":"Implemented"}
    else:
        oldValues = {"Tax Services":"Implemented"}
        newValues = {"Tax Services":"Remove Implementation"}

    return gameCycles.doNextRound(update,_,oldValues,newValues)


def handleDoNothing(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    logger.info("Doing nothing")

    return gameCycles.doNextRound(update,_,{},{})

def getDeclareWarMessage(update: Update, _: CallbackContext,warning=None) ->str:
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))
    effectiveIndex = indivK.otherActionsStates.index(indivK.DECLAREWAR)
    dicKey = list(KR.OtherActionsDict)[effectiveIndex] 
    actionClassInstance = KR.OtherActionsDict[dicKey]
    pastPresWarringKingdoms = _.user_data["Declare War on neighbouring kingdom"]
    currenlyWarringKingdoms = copy.deepcopy(_.user_data["Declared War With"]) + copy.deepcopy(_.user_data["Being Attacked By"])
    try:
        otherKingdomOptions = pgres.getOtherPlayers(query.from_user.id)
    except:
        return gameCycles.doNextRound(update,_, {},{})

    otherKingdomIds = otherKingdomOptions[0]
    otherKingdomUsernames = otherKingdomOptions[1]

    print("otherKingdoms", otherKingdomOptions)

    declarableKingdoms = [] #[[name,id,is_static],[]]

    effectiveDisplayMessage = "*{0}*".format(dicKey)
    effectiveDisplayMessage +="\n\n{0}".format(actionClassInstance.pre_req[0])
    
    effectiveDisplayMessage+="\n\n*Options*"
    keyboard = [[InlineKeyboardButton("Back to Other Action Options", callback_data=str(BACKOTHERACTIONS))]]    
    count = 1
    for landOptionNames in actionClassInstance.options:

        if(landOptionNames not in pastPresWarringKingdoms):
            landOptionsVals = actionClassInstance.options[landOptionNames]
            effectiveDisplayMessage +="\n*{0}*.{1}: Static Kingdom \nLand area {2} \nNum People {3}\n".format(count,landOptionNames, landOptionsVals.landArea, landOptionsVals.numPeople)
            keyboard.append([InlineKeyboardButton("{0}".format(landOptionNames), callback_data=str(count))])
            declarableKingdoms.append([landOptionNames,-1,True])
            count+=1

    for i in range(len(otherKingdomUsernames)):
        print(currenlyWarringKingdoms)
        if(otherKingdomUsernames[i] not in currenlyWarringKingdoms):
            effectiveDisplayMessage +="\n*{0}*.{1}'s Kingdom: Friend's Kingdom\n".format(count,otherKingdomUsernames[i])
            keyboard.append([InlineKeyboardButton("{0}'s Kingdom".format(otherKingdomUsernames[i]), callback_data=str(count))])
            declarableKingdoms.append([otherKingdomUsernames[i],otherKingdomIds[i],False])
            count+=1
    if(count==1):
        effectiveDisplayMessage+="\n~NONE~"

        
    if(warning is not None):
        effectiveDisplayMessage += "*{0}*".format(warning)

    #save options 
    _.user_data[DECLARINGWAROPTIONS] = declarableKingdoms
    reply_markup = InlineKeyboardMarkup(keyboard)    

    query.edit_message_text(
        text=effectiveDisplayMessage, reply_markup=reply_markup, parse_mode= 'Markdown'
    )
    
    return indivK.DECLAREWAR