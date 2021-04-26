EVENTCOMPLETED = 100 

from telegram.ext import  Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import logging

import KingdomResources as KR
import indivKingdomLogic as indivK 
import HandleGameCyclesUpdates as gameCycles
import RandomEventsCreation as RandEvent

import random

AVAILABLEEVENTS = "AVAILABLEEVENTS"
CURRENTEVENT = "CURRENTEVENT"
NUMJUDGINGDONE = "NUMJUDGINGDONE"

MAXBLINDJUDGING = 2

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


def randomEventsOptions(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))

    randomEventAvailable = _.user_data[AVAILABLEEVENTS]
    chosen_event_index = random.randint(0,len(randomEventAvailable)-1)
    chosenEventEffectiveIndex = randomEventAvailable[chosen_event_index]

    #do not replay this event 
    _.user_data[AVAILABLEEVENTS].pop(chosen_event_index)
    _.user_data[CURRENTEVENT] = chosenEventEffectiveIndex

    chosenEvent = RandEvent.randomEventList[chosenEventEffectiveIndex]
    
    keyboard = []       
    effectiveDisplayMessage = "*Random Event*\n*{0}*\n{1}".format(chosenEvent.name,chosenEvent.scenario)
    for i in range(len(chosenEvent.options)):
        effectiveDisplayMessage+="\n\n*Option {0}: {1}*".format(i+1,chosenEvent.options[i])
        keyboard.append([InlineKeyboardButton("Option {0}".format(i+1), callback_data=str(i))])
   
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        text=effectiveDisplayMessage, reply_markup=reply_markup,parse_mode= 'Markdown'
    )

    return indivK.RANDOMEVENTS


def handleRandomEvents(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))

    chosenEventEffectiveIndex = _.user_data[CURRENTEVENT]
    chosenEvent = RandEvent.randomEventList[chosenEventEffectiveIndex]
    chosenOptionIndex = int(query.data)

    num_juding_done = _.user_data[NUMJUDGINGDONE]

    eventEndMessage = ""

    if(chosenEvent.correctOptionIndex == chosenOptionIndex):
        gameCycles.modifySatCycleTracker(update, _,chosenEvent.name, 0, 25)
        gameCycles.modifyDaoistCycleTracker(update, _, chosenEvent.name, 0, 25)
        eventEndMessage = chosenEvent.correctOptionMessage
    else:
        #check if judging and maxed out 
        if(chosenEvent.is_judgement and num_juding_done<MAXBLINDJUDGING):
            gameCycles.modifySatCycleTracker(update, _,chosenEvent.name, 0, 10)
            eventEndMessage = chosenEvent.middleOptionMessage
        else:
            gameCycles.modifySatCycleTracker(update, _,chosenEvent.name, 0, -30)
            gameCycles.modifyDaoistCycleTracker(update, _, chosenEvent.name, 0, -30)
            eventEndMessage = chosenEvent.badOptionMessage

    if(chosenEvent.is_judgement):
        _.user_data[NUMJUDGINGDONE]= num_juding_done+ 1
        print("adding to num judingdone",_.user_data[NUMJUDGINGDONE],num_juding_done+ 1)
     
    keyboard = [[InlineKeyboardButton("Continue Playing", callback_data=str(EVENTCOMPLETED))]]    
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    effectiveDisplayMessage = "*OUTCOME*\n\n{0}".format(eventEndMessage)

    query.edit_message_text(
        text=effectiveDisplayMessage, reply_markup=reply_markup,parse_mode= 'Markdown'
    )

    return indivK.RANDOMEVENTS

def handleEventCompleted(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    logger.info("callback query data {}".format(query.data))
    
    return gameCycles.doNextRound(update,_,{},{})
