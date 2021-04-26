import logging
import json
import datetime
import postgresqlCommands as pgres
import indivKingdomLogic as indivK 
import KingdomResources as KR

from telegram.ext import  Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, CallbackContext

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import os
PORT = int(os.environ.get('PORT', 80))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TOKEN = os.getenv('TOKEN', "")
# Stages
FIRST, SECOND = range(2)
# Callback data
JOIN, TWO, THREE, FOUR = range(4)

#dictionary keys
PLAYERS = "PLAYERS"
GROUPCHATID = "GROUPCHATID"
ALLUSERS = "ALLUSERS"

#timeout in min
TIMEOUT = 15

debugging = False


connection = None
cursor = None

def start(update: Update, _: CallbackContext) -> int:

    if(update.message.chat.type == "private"):
        _.bot.sendMessage(chat_id = update.message.chat_id,text= "this game can only be started in group chats")
        return ConversationHandler.END

    """Send message on `/start`."""
    # Get user that sent /start and log his name
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    logger.info("chat id %d",update.message.chat_id)
    #_.user_data[PLAYERS] = []

    keyboard = [ [InlineKeyboardButton("Join", callback_data=str(JOIN))] ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send message with text and appended InlineKeyboard
    update.message.reply_text("Let's Play LZ Kingdom, click Join to join the game.\nYou will recieve a private chat\nWhen all users are in, someone please type /start_game", reply_markup=reply_markup,timeout =36000)
    pgres.insertGroupChatTable(update.message.chat_id)
    return FIRST
    

def join(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    print(query.from_user.username)

    user = query.from_user
    
    groupChatId = update.effective_chat.id
   
    joined_users = pgres.getJoinedUsers(groupChatId)
    ids = []
    usernames = []
    print(joined_users)
    for idUsernameT in joined_users:
        idUsername = idUsernameT.split(":")
        usernames.append(idUsername[1])
        ids.append(int(idUsername[0]))
    print(ids)
    if user.id not in ids:
        joined_users.append("{0}:{1}".format(user.id,user.username))
        _.bot.sendMessage(chat_id = user.id,text=u'🏰'+" Welcome to your Kingdom - {0} Kingdom \nLet's wait for the game to start".format(user.username))
        pgres.updateJoinedUsers(groupChatId,joined_users)
        pgres.insertUserRow(user.id,user.username,groupChatId)
        usernames.append(user.username)
        query.answer()
        query.edit_message_text( text ="Let's Play LZ Kingdom, for new players type /start to join the game.\nYou will recieve a private chat\n" + \
            "When all users are in, someone please type /start_game" + "\n\nUsers {0} have jonied the game".format(', '.join(usernames))
        )
        
    return ConversationHandler.END
def helpCommand(update: Update, _: CallbackContext) -> None:
    _.bot.sendMessage(chat_id = update.message.chat_id,text= KR.helpMessage,parse_mode= 'Markdown')

def startGame(update: Update, _: CallbackContext) -> None:
    if(update.message.chat.type == "private"):
        _.bot.sendMessage(chat_id = update.message.chat_id,text= "this game can only be started in group chats")
        return
    """Send message on `/start`."""
    # Get user that sent /start and log his name
    #logger.info("_.user_data[PLAYERS]")
    #logger.info(_.user_data[PLAYERS])
    groupChatId = update.effective_message.chat_id

    game_players = pgres.getJoinedUsers(groupChatId)
    print(game_players)
    if len(game_players)==0:
        update.message.reply_text("No users are playing the game, please send /start and join the game")       
    elif len(game_players)<1:
        update.message.reply_text("Less than 2 users playing the game, please add more users to the game")
    else:
        user = update.message.from_user
        logger.info("User %s starting the game", user.first_name)
        message = "Game starting with users"
        for players in game_players:
            message+=" {0},".format(str(players.split(":")[1]))
        message = message[:-1]
        # Send message with text and appended InlineKeyboard
        update.message.reply_text(message)
        return startIndivGames(update,_,game_players,groupChatId)


def startIndivGames(update:Update,callBackContext: CallbackContext, gamePlayers:list, group_chat_id:int):
    for players in gamePlayers:
        callBackContext.bot.sendMessage(chat_id = int(players.split(":")[0]),text="Starting the game... Please send /start_kingdom to begin")
    pgres.startGameUpdate(group_chat_id,datetime.datetime.now())
    callBackContext.job_queue.run_once(send_end_game_stats, TIMEOUT*60, context=update.message.chat_id)
    #return end(update,callBackContext)


def send_end_game_stats(context: CallbackContext):
    groupChatId = context.job.context
    try:
        game_players = pgres.getJoinedUsers(groupChatId)
    except:
        return
    if len(game_players)==0:
        return       
    elif pgres.getStartTime is None :
        return               
    else:
        finalMessage = "*OVERALL GAME RANKING*\n"
        finalMessage += getPlayerScoreBoard(groupChatId)
        finalMessage += "\n\n"
        finalMessage += u"Figured out the rules of the game yet? 🤔"

        context.bot.send_message(chat_id=groupChatId, text=finalMessage,parse_mode= 'Markdown')



def getRankings(update: Update, _: CallbackContext) -> None:
    if(update.message.chat.type == "private"):
        _.bot.sendMessage(chat_id = update.message.chat_id,text= "this command can only be used in group chats")
        return ConversationHandler.END
    
    groupChatId = update.effective_message.chat_id

    game_players = pgres.getJoinedUsers(groupChatId)
    print(game_players)
    if len(game_players)==0:
        update.message.reply_text("No users are playing the game, please send /start and join the game")       
    elif pgres.getStartTime is None :
        update.message.reply_text("Game has not started, please send /start_game to start the game")       
    elif pgres.getStartedGame(game_players[0].split(":")[0]):
        update.message.reply_text("Please wait for all players' game to end and try sending /get_rankings again")       
    else:
        finalMessage = "*OVERALL GAME RANKING*\n"
        finalMessage += getPlayerScoreBoard(groupChatId)
        finalMessage += "\n"
        finalMessage += u"Figured out the rules of the game yet? 🤔"
        
        update.message.reply_text(finalMessage,parse_mode= 'Markdown')


def getPlayerScoreBoard(group_id:int) ->str:
    joined_users = pgres.getJoinedUsers(group_id)
    ids = []
    usernames = []
    print(joined_users)
    for idUsernameT in joined_users:
        idUsername = idUsernameT.split(":")
        usernames.append(idUsername[1])
        ids.append(int(idUsername[0]))
    print(ids)
    
    playerScores = {}

    for i in range(len(ids)):
        playerScores[usernames[i]] =  pgres.getDaoistSatScore(ids[i])
    sortedKeys = sorted(playerScores.keys(), key=lambda x: (playerScores[x][0], playerScores[x][1]), reverse=True)

    rank =1
    
    scoreMessage = ""
    for player in sortedKeys:
        scoreMessage +="\n{0}. {1}: Points - {2} Satisfaction Score - {3}".format(rank,player,playerScores[player][0], playerScores[player][1])
        scoreMessage += u' 🏰'
        scoreMessage += "\n"
        rank+=1
    print("deleting chat", group_id)
    pgres.deleteGroupAndPlayers(group_id)
    return scoreMessage


def end(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.edit_message_text(text="Game has Started \nHave Fun!")
    return ConversationHandler.END

def main() -> None:
    # Create the Updater and pass it your bot's token.
    
    updater = Updater(TOKEN)
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    try:
        pgres.postgresConnection()

        # Use the pattern parameter to pass CallbackQueries with specific
        # data pattern to the corresponding handlers.
        # ^ means "start of line/string"
        # $ means "end of line/string"
        # So ^ABC$ will only allow 'ABC'
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                FIRST: [
                    CallbackQueryHandler(join, pattern='^' + str(JOIN) + '$'),
                ]
            },
            fallbacks=[CommandHandler('start', start)],
        )

        # Add ConversationHandler to dispatcher that will be used for handling updates
        dispatcher.add_handler(conv_handler)
        dispatcher.add_handler(CommandHandler("start_game", startGame,pass_job_queue=True))    # Start the Bot Game
        dispatcher.add_handler(indivK.getIndivConversationHandler())
        dispatcher.add_handler(CommandHandler("get_rankings", getRankings))
        dispatcher.add_handler(CommandHandler("help", helpCommand))
        if debugging:
            updater.start_polling()
        else:
            updater.start_webhook(listen="0.0.0.0",
                            port=int(PORT),
                            url_path=TOKEN,
                            webhook_url='https://agile-sands-44709.herokuapp.com/' + TOKEN
                            )
            #updater.bot.setWebhook('https://agile-sands-44709.herokuapp.com/' + TOKEN)
        
        # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT
        updater.idle()
    except Exception as e: print(e)        
    finally:
        #pgres.debugDeleteAllFromPosgres()
        pgres.closePosgres()


if __name__ == '__main__':
    main()