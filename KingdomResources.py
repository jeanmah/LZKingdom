class generalVariable:
    initVal = 0
    units = ""
    category = False
    categoryMax = {}
    def __init__(self, initVal, units,category=False,categoryMax=None):
        self.initVal = initVal
        if units!=None:
            self.units = units
        self.category = category
        self.categoryMax = categoryMax

class statVariable(generalVariable):
    statName = ""
    def __init__(self,statName, initVal, units,category=False,categoryMax=None):
        super().__init__(initVal,units,category,categoryMax)
        self.statName = statName

class infraVariable(generalVariable):
    infraName = ""
    def __init__(self,infraName, initVal, units,category=False,categoryMax=None):
        super().__init__(initVal,units,category,categoryMax)
        self.infraName = infraName

class ActionClass:
    options = []
    pre_req = {}
    scoring = {}
    defaultOption = None
    displayMessage = ""
    def __init__(self,options,pre_req,scoring,defaultOption,displayMessage=""):
        self.options = options
        self.pre_req = pre_req
        self.scoring = scoring
        self.defaultOption = defaultOption
        self.displayMessage = displayMessage

class ValuesClass(ActionClass):
    def __init__(self, pre_req, scoring):
        super().__init__(["Promote","Stop Promoting"], pre_req, scoring,"Would you like to promote this value to the masses?")

class StaticResources:
    is_claimed = False
    landArea = 0
    numPeople = 0
    def __init__(self,landArea,numPeople,is_claimed = False):
        self.landArea = landArea
        self.numPeople = numPeople
        self.is_claimed = is_claimed


moralValues = [ "wisdom", "intelligence", "fillial piety", "loyalty"]

#Stats 
statsDict = { 
    "DaoistPoints" : statVariable("Points",1000,"points"), 
    "PeopleSatisfaction" : statVariable("People Satisfaction",200,"",True,{"Very Dissatisfied":100,"Dissatisfied": 200, "Indifferent":300,"Satisfied":400}),
    "NumVillagers": statVariable("Num Villagers",20,"people"), 
    "KingdomMoney" : statVariable("Kingdom Money",500,"bubi"), 
    "MilitaryPower" : statVariable("Military Power",10,"power",True,{"Small":1000,"Medium":2000,"Large":3000}), 
    "Beauty" : statVariable("Beauty",10,"Beauty",True,{"Small":1000,"Medium":2000,"Large":3000}), 
    "taxAmount" : statVariable("Tax Amount",10,"bubi"), 
    "averageVillagersEarnings" : statVariable("Ave Villagers Earnings",10,"bubi"),
    "taxServices" : statVariable("Tax Services",False,"Used/Not Used"),
    "declaredWarWith" : statVariable("Declared War With",[],None),
    "beingAttackedBy" :  statVariable("Being Attacked By",[],None),
    "amountOfLand" : statVariable("Amt Of Land",100,"hectares"),
    "valuesPromoted" : statVariable("Values Promoted",[], None),
}

#infrastructure
infraDict = {
    "Military Power" : infraVariable("Military Power",10,"power",True,{"Small":1000,"Medium":2000,"Large":3000}), 
    "Farms" : infraVariable("Farms",40,"Farms",True,{"Small":1000,"Medium":2000,"Large":3000}), 
    "Fishing Infrastructure" : infraVariable("Fishing Infrastructure",False,"Have/Do not have"), 
    "Palace Grandeur" : infraVariable("Palace Grandeur",10,"",True,{"Very Simple":1000,"Pretty": 2000, "Grand":3000}),
    "Higher schools" : infraVariable("Higher schools",False,"Have/Do not have"), 
    "Apprenticeships" : infraVariable("Apprenticeships",False,"Established/Not Established"), 
    "Music Schools" : infraVariable("Music Schools",False,"Have/Do not have"), 
    "Iron Production Places" : infraVariable("Iron Production Places",0,"Iron Production Places",True,{"Small":400,"Medium":800,"Large":1200}), 
}

staticKingdomDict = {
    "Kingdom of Water": StaticResources(100, 20, True),
    "Kingdom of Earth": StaticResources(100, 20, True),
    "Kingdom of Air": StaticResources(100, 20, True),
    "Kingdom of Fire": StaticResources(100, 20, True),
}

staticUnclaimedLandDict = {
    "Unclaimed North": StaticResources(100, 10),
    "Unclaimed South": StaticResources(100, 10),
    "Unclaimed East": StaticResources(100, 10),
    "Unclaimed West": StaticResources(100, 10),
}

InfraActionsDict = {
    "Increase Military Spending": ActionClass([0,0.2,0.4,0.6,0.8,1.0], [], [],0.0,"How would you like to increase Military Spending?\n\nIt is a fraction of your Taxed Money"),
    "Build Farms": ActionClass([0.2,0.4,0.6,0.8], [], [], 0.2,"How would you like to expand your Farms?\n\nIt is a fraction of your Kingdom's land area"),
    "Build Fishing Infrastructure": ActionClass(["Build","Don't Build"], [], [], "Don't Build", "Do you want to provide your villagers better fishing infrastructure?"),
    "Beautify Palace" : ActionClass(["Increase beauty by 200","Decrease beauty by 200"], ["Requries 100 bubi or 50 bubi if Tax Services are established"], [], None, "Do you wish to beautify your palace, foritifications are beautiful too..."),
    "Build Higher Schools": ActionClass(["Build","Don't Build"], ["Requries 100 bubi or 50 bubi if Tax Services are established"], [], "Don't Build", "Do you wish to give your villagers an education in Math, Science, Philosophy and the like"),
    "Establish Apprenticeships" : ActionClass(["Establish","Don't Establish"], ["Requries 100 bubi or 50 bubi if Tax Services are established"], [], "Don't Establish", "Do you wish to encourage your villagers to learn new skills from experienced masters?\n\nThey would make better soliders, farmers and iron production workers"),
    "Build Music Schools" : ActionClass(["Build","Don't Build"], ["Requries 100 bubi or 50 bubi if Tax Services are established"], [], "Don't Build", "Do you wish to give your villagers an education in Music?"),
    "Build Iron Production Places" : ActionClass([0.0,0.2,0.4,0.6,0.8], [], [], 0.0,"Would you like to expand iron production?\n\nIt is a fraction of your Kingdom's land area\n\nIron increases Military and Farming Productivity"),
}

OtherActionsDict = {
    "Values Promoted": ActionClass(moralValues, [], [],[],"Which of these values would you like to promote and instill into your people"),
    "Declare War on neighbouring kingdom" :ActionClass(staticKingdomDict, ["You need a military score of at least 500 to declare war on someone", "You cannot declare war on someone who declare war on you first"], [],[],"Declare war on your friends and other kingdoms.\n If you win, their villagers and their land will belong to you"),
    "Occupy unclaimed land": ActionClass(staticUnclaimedLandDict, [], [],[],"There are some unclaimed land with people living there. \nChoose which of these areas you would like to peacefully integrate the people and their land into your kingdom."),
    "Increase taxes": ActionClass(["Increase taxes by 10","Decrease taxes by 10"], [], [],None,"Taxes are collected from every villager every 5 rounds \nThe money will then be used to pay for projects"),
    "Implement tax services" :ActionClass(["Implement","Do not implement"], [], [],"Do not implement", "Let your people do community work as part of their taxes. \nBuilding infrastructure will then cost less money."),
    "Do Nothing": ActionClass(["Do nothing"], [], [],None, "If you are happy with the way things are now, why change it? \nSkip a round"),
}


EndOfWarOptions = ["Celebrate the end of the war","Plunder the newly acquired Kingdom","Mourn all the dead"]
EndOfWarMessages = ["Your people are glad for a celebration\nbut the people of the other kingdom don't accept you as their ruler",\
    "Many people see you as inhumane and have left your Kingdom",\
    "Your people and your newly aquired people pay respects to the dead.\nThey are glad to see a ruler who respects human life"
    ]

helpMessage = \
"""
*HELP*
Add this bot to a group chat and ensure that all users have started a chat with the bot (bots cannot initialize chats with real people).

Make each user send 'start' to bot in the group chat and click the button ‘join’ when prompted.

When each user clicks ‘join’, the bot will send them a private message telling them to wait for the game to start.

When all users are present, send 'start game' to the bot in the group chat. All joined users will then receive a private message telling them to send 'start kingdom' to begin the game. The game times out after 15 minutes.

After sending 'start kingdom', users can view their Kingdom statistics and click on the inline keyboards to execute actions. 

After the game, players should head back to the group chat to view who has won. Players will be prompted to type 'get rankings' to view the rankings if the game was not ended by a timeout of 15 minutes. 
"""
instructionsMessage = \
"""
*INSTRUCTIONS*

STATS
You may view your Kingdom’s Statuses on the Home page or under “Other Actions”. 
Your stats give you an idea of how your Kingdom is faring, if any wars are going on and others. 
Do actions to change your stats. Some of your stats are automatically computed from other statuses and will vary from cycle to cycle

INFRASTRUCTURE
You may view your Kingdom’s Infrastructures on the Home page or under “Build Infrastructure”. 
Your infrastructures affect your Kingdom’s status. 

ACTIONS
Actions affect your Kingdom’s status and infrastructure. 
They can be completed by clicking on the in-line keyboard. 
Executing an action would lead to the end of a cycle.

DECLARING WAR 
Declaring war is done under “Other Actions”. 
You may only declare wars if your military power is above 500. 
There are 4 static Kingdoms that are available to all at the start. 
You may declare war on these kingdoms and your friends’ kingdoms. 
The declaration of war on your friend’s side will be reflected on their next cycle. 
The other kingdom’s onto which you have declared war will be reflected in your Kingdom’s status. 
You may withdraw from a war that you have started in the War Room. 
Withdrawn wars may be started again. 
In the War Room, you will also notice Kingdom’s that have started Diplomacy with you. 
You may choose to accept them and this will result in your immediate withdrawal from the war. 

BEING ATTACKED
The Kingdoms that have attacked you will be reflected on your Kingdom’s status. 
You may start diplomacy on these Kingdoms in the hope that they will withdraw from your kingdom. 

WINNING A WAR
Wars are won against Static Kingdoms when your points are above 1100 or after 5 cycles. 
Wars are won against other players when the attacking player has points less than 150 of the defending player. 

LOSING A WAR
Players immediately lose a war if their points are below a certain amount. 
The loss of a player to any war will result in the end of the game. 
Players will notice that the game has ended in the next cycle.

RANDOM EVENTS
At the end of a cycle, there might be random events where you people come to you for answers. 
You have to make choices. There are correct and wrong choices. 

CYCLES
A game cycle ends when the player has taken an action. 
A player may choose to “Do Nothing” under the “Other Actions” page to end a cycle as well. 
The Kingdom Status is recomputed at the end of every cycle and these differences will be reflected in the next page. 

LOSING
Players lose when they have lost a war or if all their villagers leave the Kingdom. 
Villagers come and go depending on how satisfied the villagers are. 
One player losing the game will lead to the game ending for all players. 

GAME END
The game ends when a player loses, if a player ends the game in the Home page or if the game has timed out. 
The game times out 15 minutes after the start of the game. Players should head back to the group chat to view who has won. 
Players will be prompted to type 'get rankings' to view the rankings if the game was not ended by a timeout. 
"""