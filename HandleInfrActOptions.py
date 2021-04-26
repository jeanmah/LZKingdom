BACKINFRA, OPTION1, OPTION2, OPTION3, OPTION4, OPTION5, OPTION6, OPTION7, OPTION8, OPTION9, OPTION10 = range(11)

from telegram.ext import  Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import logging

import KingdomResources as KR
import indivKingdomLogic as indivK 
import HandleGameCyclesUpdates as gameCycles

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

apprenticeshipMilitaryBonus = 500
apprenticeshipFarmBonus = 500
apprenticeshipIronBonus = 50

IronBonusFraction = 2

def handleIncMilSpending(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))
    infraActionInstance= KR.InfraActionsDict["Increase Military Spending"]
    fractionOfSateMoney = infraActionInstance.options[int(query.data)-1]
    _.user_data["Increase Military Spending"] = fractionOfSateMoney

    updatedMilitaryScore,oldValues,newValues = updateMilitaryScore(update,_)
    if updatedMilitaryScore>1500:
        gameCycles.modifyDaoistCycleTracker(update,_,"Military",0,-10)
        gameCycles.modifySatCycleTracker(update,_,"Military",3,20)
    else:
        gameCycles.removeFromDaoistCycleTracker(update, _, "Military")
    
    return gameCycles.doNextRound(update,_,oldValues,newValues)

def handleBuildFarm(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))

    #Farm score based on fraction * land area *2 + apprenticeship bonus + Iron bonus 

    infraActionInstance= KR.InfraActionsDict["Build Farms"]
    fractionOfLand = infraActionInstance.options[int(query.data)-1]

    #Farm Fraction + Iron Fraction =0.8
    if(not checkValidFarmIron(fractionOfLand,_.user_data["Build Iron Production Places"])):
        current_chosen_option = _.user_data["Build Farms"]
        query.edit_message_text(
            text="{0}\nThe current chosen option is {1}\nFarming and Iron Production should take <= 0.8 of the land area". \
                format(infraActionInstance.displayMessage,current_chosen_option), reply_markup=query.message.reply_markup,parse_mode= 'Markdown'
        )
        return indivK.BUILDFARM
    
    _.user_data["Build Farms"] = fractionOfLand
    updatedFarmScore, oldValues, newValues = updateFarmScore(update,_)

    if updatedFarmScore>1500:
        gameCycles.modifyDaoistCycleTracker(update,_,"Farm",0,-10)
    else:
        gameCycles.removeFromDaoistCycleTracker(update, _, "Farm")
    
    return gameCycles.doNextRound(update,_,oldValues,newValues)

def handleBuildFish(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))
    infraActionInstance= KR.InfraActionsDict["Build Fishing Infrastructure"]
    buildDemolish = infraActionInstance.options[int(query.data)-1]

    _.user_data[KR.infraDict["Fishing Infrastructure"].infraName] = int(query.data)-1 ==0
    _.user_data["Build Fishing Infrastructure"] = buildDemolish

    aveEarning, oldValues, newValues = updateAveEarning(update,_)

    return gameCycles.doNextRound(update,_,oldValues,newValues)

def handlebeautifyPalace(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    minMoney = 100
    minMoneyWithService = 50

    logger.info("callback query data {}".format(query.data))
    infraActionInstance= KR.InfraActionsDict["Beautify Palace"]

    infraVarInstance = KR.infraDict["Palace Grandeur"]
    maxPossible = infraVarInstance.categoryMax[list(infraVarInstance.categoryMax)[len(infraVarInstance.categoryMax)-1]]

    currentBeauty = _.user_data["Beauty"]

    oldValues = {"Beauty": currentBeauty}

    if(int(query.data)-1 == 0): # increase
        if(currentBeauty>maxPossible):
            current_chosen_option = _.user_data["Beautify Palace"]
            query.edit_message_text(
                text="{0}\nThe current beauty level is {1}\nYou have already reached the max beautification level". \
                    format(infraActionInstance.displayMessage,currentBeauty), reply_markup=query.message.reply_markup, parse_mode= 'Markdown'
            )
            return indivK.BEAUTIFYPALACE
        if(checkEnoughMoney(minMoney,minMoneyWithService,_)):    #checks and deducts 
            currentBeauty+=200
            currentBeauty = min(currentBeauty,maxPossible)
            if(currentBeauty<1000):
                gameCycles.modifySatCycleTracker(update, _, "Beauty", 3, 5)
            else:
                gameCycles.modifyDaoistCycleTracker(update, _, "Beauty", 0, -1)
        else:
            current_chosen_option = _.user_data["Beautify Palace"]
            query.edit_message_text(
                text="{0}\nThe current beauty level is {1}\nYou do not have enough money to do this action". \
                    format(infraActionInstance.displayMessage,currentBeauty), reply_markup=query.message.reply_markup, parse_mode= 'Markdown'
            )
            return indivK.BEAUTIFYPALACE
    else:
        currentBeauty-=200
        if(currentBeauty<1000 and currentBeauty>=0):
            gameCycles.modifyDaoistCycleTracker(update, _, "Beauty", 0, 1)
        currentBeauty  = max(0,currentBeauty)

    _.user_data["Beauty"] = currentBeauty
    _.user_data["Beautify Palace"] = currentBeauty
    _.user_data["Palace Grandeur"] = currentBeauty

    newValues = {"Beauty": currentBeauty}

    return gameCycles.doNextRound(update,_,oldValues,newValues)
    
def handleBuildHigherSchool(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()

    minMoney = 100
    minMoneyWithService = 50

    logger.info("callback query data {}".format(query.data))
    infraActionInstance= KR.InfraActionsDict["Build Higher Schools"]
    buildDemolish = infraActionInstance.options[int(query.data)-1]

    if(int(query.data)-1 == 0): # build
        if(not checkEnoughMoney(minMoney,minMoneyWithService,_)):    #checks and deducts 
            current_chosen_option = _.user_data["Build Higher Schools"]
            query.edit_message_text(
                text="{0}\nThe current chosen option is {1}\nYou do not have enough money to do this action". \
                    format(infraActionInstance.displayMessage,current_chosen_option), reply_markup=query.message.reply_markup,parse_mode= 'Markdown'
            )
            return indivK.HIGHERSCH
    is_building =  int(query.data)-1 ==0
    _.user_data[KR.infraDict["Higher schools"].infraName] = is_building
    _.user_data["Build Higher Schools"] = buildDemolish

    if(is_building):
        gameCycles.modifySatCycleTracker(update, _, "HigherSchools", 3, 10) 
        gameCycles.modifyDaoistCycleTracker(update, _, "HigherSchools", 3, -10)
    else:
        gameCycles.removeFromSatCycleTracker(update, _, "HigherSchools")
        gameCycles.modifyDaoistCycleTracker(update, _, "HigherSchools", 0, 10)

    if(is_building):
        OldValues = {"Higher Schools":"Not Built"}
        NewValues = {"Higher Schools":"Built"}
    else:
        OldValues = {"Higher Schools":"Built"}
        NewValues = {"Higher Schools":"Demolish"}
    return gameCycles.doNextRound(update,_, OldValues, NewValues)

def handleEstablishApprentiships(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))
    infraActionInstance= KR.InfraActionsDict["Establish Apprenticeships"]
    buildDemolish = infraActionInstance.options[int(query.data)-1]

    minMoney = 100
    minMoneyWithService = 50
    
    is_building = int(query.data)-1 == 0

    if(is_building): # build
        if(not checkEnoughMoney(minMoney,minMoneyWithService,_)):    #checks and deducts 
            current_chosen_option = _.user_data["Establish Apprenticeships"]
            query.edit_message_text(
                text="{0}\nThe current chosen option is {1}\nYou do not have enough money to do this action". \
                    format(infraActionInstance.displayMessage,current_chosen_option), reply_markup=query.message.reply_markup,parse_mode= 'Markdown'
            )
            return indivK.ESTAPPR

    _.user_data[KR.infraDict["Apprenticeships"].infraName] = is_building
    _.user_data["Establish Apprenticeships"] = buildDemolish

    if(is_building):
        oldValues = {"Apprentiships":"Not Established"}
        newValues = {"Apprentiships":"Established"}
    else:
        oldValues = {"Apprentiships":"Established"}
        newValues = {"Apprentiships":"Remove Establishment"}

    score, miloldValues, milnewValues = updateMilitaryScore(update,_)
    score, FarmOldValues, FarmNewValues = updateFarmScore(update,_)
    score, IronOldValues, IronNewValues = updateIronScore(update,_)

    oldValues.update(miloldValues)
    oldValues.update(FarmOldValues)
    oldValues.update(IronOldValues)
    newValues.update(milnewValues)
    newValues.update(FarmNewValues)
    newValues.update(IronNewValues)

    return gameCycles.doNextRound(update,_,oldValues,newValues)


def handleBuildMusic(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))
    infraActionInstance= KR.InfraActionsDict["Build Music Schools"]
    buildDemolish = infraActionInstance.options[int(query.data)-1]
    minMoney = 100
    minMoneyWithService = 50

    if(int(query.data)-1 == 0): # build
        if(not checkEnoughMoney(minMoney,minMoneyWithService,_)):    #checks and deducts 
            current_chosen_option = _.user_data["Build Music Schools"]
            query.edit_message_text(
                text="{0}\nThe current chosen option is {1}\nYou do not have enough money to do this action". \
                    format(infraActionInstance.displayMessage,current_chosen_option), reply_markup=query.message.reply_markup,parse_mode= 'Markdown'
            )
            return indivK.MUSICSCH
    is_building = int(query.data)-1 ==0
    _.user_data[KR.infraDict["Music Schools"].infraName] = is_building
    _.user_data["Build Music Schools"] = buildDemolish

    if(is_building):
        gameCycles.modifySatCycleTracker(update, _, "HigherSchools", 3, 10) 
        gameCycles.modifyDaoistCycleTracker(update, _, "HigherSchools", 3, -10)
    else:
        gameCycles.removeFromSatCycleTracker(update, _, "HigherSchools")
        gameCycles.modifyDaoistCycleTracker(update, _, "HigherSchools", 0, 10)

    if(is_building):
        OldValues = {"Music Schools":"Not Built"}
        NewValues = {"Music Schools":"Built"}
    else:
        OldValues = {"Music Schools":"Built"}
        NewValues = {"Music Schools":"Demolish"}

    return gameCycles.doNextRound(update,_, OldValues, NewValues)

def handleBuildIron(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))

    #Iron score based on fraction * land area + iron apprenticeship bonus 

    infraActionInstance= KR.InfraActionsDict["Build Iron Production Places"]
    fractionOfLand = infraActionInstance.options[int(query.data)-1]

    #Farm Fraction + Iron Fraction =0.8
    if(not checkValidFarmIron(_.user_data["Build Farms"],fractionOfLand)):
        current_chosen_option = _.user_data["Build Iron Production Places"]

        query.edit_message_text(
            text="{0}\nThe current chosen option is {1}\nFarming and Iron Production should take <= 0.8 of the land area". \
                format(infraActionInstance.displayMessage,current_chosen_option), reply_markup=query.message.reply_markup,parse_mode= 'Markdown'
        )
        return indivK.BUILDIRON

    _.user_data["Build Iron Production Places"] = fractionOfLand

    updatedIronScore, OldValues, NewValues = updateIronScore(update,_)

    score, MilOldValues, MilNewValues = updateMilitaryScore(update,_)
    score, FarmOldValues, FarmNewValues = updateFarmScore(update,_)

    OldValues.update(FarmOldValues)
    OldValues.update(MilOldValues)
    NewValues.update(FarmNewValues)
    NewValues.update(MilNewValues)

    if updatedIronScore>600:
        gameCycles.modifyDaoistCycleTracker(update,_,"Iron",0,-10)
    else:
        gameCycles.removeFromDaoistCycleTracker(update, _, "Iron")

    return gameCycles.doNextRound(update,_,OldValues,NewValues)


def checkValidFarmIron(farmFrac, ironFrac):
    return farmFrac+ironFrac<=0.8

def checkEnoughMoney(minMoney:int,minMoneyWithService:int,_:CallbackContext):
    currentAmount = _.user_data[KR.statsDict["KingdomMoney"].statName]
    hasTaxService = _.user_data[KR.infraDict["Apprenticeships"].infraName]
    if(hasTaxService):
        if(currentAmount<minMoneyWithService):
            return False
        currentAmount -= minMoneyWithService
    else:
        if(currentAmount<minMoney):
            return False
        currentAmount -=minMoney
    _.user_data[KR.statsDict["KingdomMoney"].statName] = currentAmount
    return True

def updateMilitaryScore(update: Update, _: CallbackContext) -> int:
    #Military score based on fraction * kingdom taxes*2 + apprenticeship bonus + Iron bonus"
    fractionOfSateMoney = _.user_data["Increase Military Spending"]
    currentTaxes = _.user_data["Tax Amount"] 
    numVillagers = _.user_data["Num Villagers"] 
    totalMilitaryScore = fractionOfSateMoney* currentTaxes * numVillagers *2
    
    #apprentiship bonus
    if( _.user_data[KR.infraDict["Apprenticeships"].infraName]):
        totalMilitaryScore+=apprenticeshipMilitaryBonus

    #iron bonus
    totalMilitaryScore+=IronBonusFraction*int(_.user_data[KR.infraDict["Iron Production Places"].infraName])
    infraVarInstance = KR.infraDict["Military Power"]
    maxPossible = infraVarInstance.categoryMax[list(infraVarInstance.categoryMax)[len(infraVarInstance.categoryMax)-1]]
    print("military power",_.user_data[infraVarInstance.infraName])

    oldValues = {"Military Power": _.user_data[infraVarInstance.infraName]}

    updatedMilitaryScore = int(min(totalMilitaryScore,maxPossible))

    newValues = {"Military Power": updatedMilitaryScore}

    _.user_data[infraVarInstance.infraName] = updatedMilitaryScore

    return (updatedMilitaryScore,oldValues,newValues)

    
def updateFarmScore(update: Update, _: CallbackContext) ->tuple :
    #Farm score based on fraction * land area *2 + apprenticeship bonus + Iron bonus 

    fractionOfLand = _.user_data["Build Farms"]

    land_area = _.user_data[KR.statsDict["amountOfLand"].statName]
    totalFarmScore = fractionOfLand* land_area*2
    
    #apprentiship bonus
    if( _.user_data[KR.infraDict["Apprenticeships"].infraName]):
        totalFarmScore+=apprenticeshipFarmBonus

    #iron bonus
    totalFarmScore+=IronBonusFraction*int(_.user_data[KR.infraDict["Iron Production Places"].infraName])

    infraVarInstance = KR.infraDict["Farms"]
    maxPossible = infraVarInstance.categoryMax[list(infraVarInstance.categoryMax)[len(infraVarInstance.categoryMax)-1]]
    
    oldValues = {"Farm Points": _.user_data[infraVarInstance.infraName]}

    updatedFarmScore = int(min(totalFarmScore,maxPossible))

    newValues = {"Farm Points": updatedFarmScore}

    _.user_data[infraVarInstance.infraName] = updatedFarmScore

    ave_score, appendingOldValues, appendingNewValues = updateAveEarning(update,_)

    oldValues.update(appendingOldValues)
    newValues.update(appendingNewValues)

    return (updatedFarmScore,oldValues,newValues)


def updateIronScore(update: Update, _: CallbackContext) ->tuple:
    #Iron score based on fraction * land area + iron apprenticeship bonus 

    fractionOfLand = _.user_data["Build Iron Production Places"]

    land_area = _.user_data[KR.statsDict["amountOfLand"].statName]
    totalIronScore = fractionOfLand* land_area
    
    #apprentiship bonus
    if( _.user_data[KR.infraDict["Apprenticeships"].infraName]):
        totalIronScore+=apprenticeshipIronBonus

    infraVarInstance = KR.infraDict["Iron Production Places"]
    maxPossible = infraVarInstance.categoryMax[list(infraVarInstance.categoryMax)[len(infraVarInstance.categoryMax)-1]]
    
    oldValues = {"Iron Points": _.user_data[infraVarInstance.infraName]}

    updatedIronScore = int(min(totalIronScore,maxPossible))
    
    newValues = {"Iron Points": updatedIronScore}

    _.user_data[infraVarInstance.infraName] = updatedIronScore
    
    ave_score, appendingOldValues, appendingNewValues = updateAveEarning(update,_)

    oldValues.update(appendingOldValues)
    newValues.update(appendingNewValues)

    return (updatedIronScore,oldValues,newValues)


def updateAveEarning(update: Update, _: CallbackContext) -> tuple:
    #ave earning = fishing*5+farming points/100+iron/10
    has_fishing = _.user_data[KR.infraDict["Fishing Infrastructure"].infraName]
    farming_points  = _.user_data["Farms"]
    iron_points  = _.user_data["Iron Production Places"]

    oldValues = {"Ave Villagers Earnings": _.user_data["Ave Villagers Earnings"]}
    new_earnings = int(has_fishing*5+farming_points/10+ iron_points/5)
    newValues = {"Ave Villagers Earnings": new_earnings}

    _.user_data["Ave Villagers Earnings"] = new_earnings

    return (new_earnings,oldValues,newValues)