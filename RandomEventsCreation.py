class RandomEvent:
    name:str = ""
    scenario:str = ""
    options:list = []
    correctOptionIndex:int = 0
    correctOptionMessage = ""
    badOptionMessage = ""
    middleOptionMessage = ""
    is_judgement = False

    def __init__(self,name:str, is_judgement=False):
        self.name = name
        self.is_judgement = is_judgement


#judement event 1
childStoleAppleEvent = RandomEvent("A Child Is Caught Stealing", True)
childStoleAppleEvent.scenario = \
"""
A man brings a child to you and explains that the child stole an apple from his garden

He wants you to punish the child

What do you do?
"""
childStoleAppleEvent.options = ["Punish the child","Delegate this issue to one of your trusted officials well-versed in the laws", "Give the child another chance and let the chidl go"]
childStoleAppleEvent.correctOptionIndex =1
childStoleAppleEvent.correctOptionMessage = "The case was handled expertly by the official"
childStoleAppleEvent.badOptionMessage = "Your villagers have started to expect more from you and are split by een your decision"
childStoleAppleEvent.middleOptionMessage = "The villagers appreciate your input"

#judement event 2
personStoleFromMerchantEvent = RandomEvent("A Farmer Stole from a Merchant", True)
personStoleFromMerchantEvent.scenario = \
"""
A merchant drags a farmer to you and accuses the farmer of stealing some gold from him

He wants you to severly punish the farmer

What do you do?
"""
personStoleFromMerchantEvent.options = ["Delegate this issue to one of your trusted officials well-versed in the laws", "Severly punish the farmer", "Lightly punish the farmer",  "Give the farmer another chance and let the farmer go"]
personStoleFromMerchantEvent.correctOptionIndex =0
personStoleFromMerchantEvent.correctOptionMessage = "The case was handled expertly by the official"
personStoleFromMerchantEvent.badOptionMessage = "Your villagers have started to expect more from you and are split by your decision"
personStoleFromMerchantEvent.middleOptionMessage = "The villagers appreciate your handling of the case"


#judement event 3
beatingWifeEvent = RandomEvent("A man is Caught Beating his Wife", True)
beatingWifeEvent.scenario = \
"""
A badly injured lady comes to you and explains that her husband had beat her

She wants you to arrest her husband and issue a divorse 

What do you do?
"""
beatingWifeEvent.options = ["Severly punish the husband as you see fit", "Punish the husband as the lady asks", "Delegate this issue to one of your trusted officials well-versed in the laws",  "Give the husband another chance and let the husband go"]
beatingWifeEvent.correctOptionIndex =2
beatingWifeEvent.correctOptionMessage = "The case was handled expertly by the official"
beatingWifeEvent.badOptionMessage = "Your villagers have started to expect more from you and are split by your decision"
beatingWifeEvent.middleOptionMessage = "The villagers appreciate your handling of the case"

#judement event 4
taxesEvent = RandomEvent("A Person has not paid their taxes for months", True)
taxesEvent.scenario = \
"""
An official brings to you a person who has been evading their taxes for months

The official wants you to punish the tax evader

What do you do?
"""
taxesEvent.options = ["Punish the tax evader", "Delegate this issue to one of your trusted officials well-versed in the laws",  "Give the tax evader another chance and let them go"]
taxesEvent.correctOptionIndex =1
taxesEvent.correctOptionMessage = "The case was handled expertly by the official"
taxesEvent.badOptionMessage = "Your villagers have started to expect more from you and are split by your decision"
taxesEvent.middleOptionMessage = "The villagers appreciate your handling of the case"


#corrupted frient event
corruptedFriendEvent = RandomEvent("Close Advisor Friend is Corrupt", False)
corruptedFriendEvent.scenario = \
"""
It has been brought to your attention that a close friend of yours who is also one of your advisors has been accepting bribes

You know that your friend is the sole-provider for a family of 8 and they will not be able to get another government job if you fire them. 

What do you do?
"""
corruptedFriendEvent.options = ["Fire your friend", "Give your friend another chance and let them continuing working with you"]
corruptedFriendEvent.correctOptionIndex =0
corruptedFriendEvent.correctOptionMessage = "You handled the case objectively and your villagers appreciate it"
corruptedFriendEvent.badOptionMessage = "Your villagers are split by your decision and feel that you were showing favouritism"


#clan disput event
clanDispute = RandomEvent("Private Dispute between Clans", False)
clanDispute.scenario = \
"""
You noticed that 2 of the clans in your village are fighting. 

What do you do?
"""
clanDispute.options = ["Trust that they will sort it out", "Intervene and stop the fighting before it escalates"]
clanDispute.correctOptionIndex =0
clanDispute.correctOptionMessage = "Without your intervention, the clans came to an agreement and have stopped fighting"
clanDispute.badOptionMessage = "Both clans do not appreciate you meddling in their private affairs. \
    \nMoreover, your decision showed a lack of understanding of what was happening within each clan"


#bandits event
banditsEvent = RandomEvent("Bandits have Plundered Part of your Kingdom", False)
banditsEvent.scenario = \
"""
Your villagers ask you to protect them from the bandits near the edge of your Kingdom

What do you do?
"""
banditsEvent.options = ["Task your villagers to build a wall around the village", "Command the increase of weapon forging", "Delegate this issue to a general", "Do nothing"]
banditsEvent.correctOptionIndex =2

banditsEvent.correctOptionMessage = "Your general has handled the issue expertly and the bandits have stop coming"
banditsEvent.badOptionMessage = "Your efforts were not enough and were not effective. \nThe bandits continue to attack your kingdom"


randomEventList = [childStoleAppleEvent,personStoleFromMerchantEvent, \
    beatingWifeEvent,taxesEvent, corruptedFriendEvent,clanDispute, banditsEvent]