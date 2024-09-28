''' TO DO
1) update the frequency you can encounter certain events (shop more rare fx)
3) update the map to show symbols symbolizing what events occured to the player
4) refactor text to make it look better
5) add more random events
6) GIANT EVENT: når treffer en kroppsdel -> skaden går opp, og accuracy ned (begge går ned as of now)
6) add an exception to the 'entydighet', program fails if there is a spelling error, for instance 'wsait' instead of 'waist'
7) fix the staff stuff, or just remove it completely
8) gjøre noe med Totems?
9) hindre at EIDE attributes på våpen dukker opp i shoppen, man kan ikke kjøpe 2 av samme altså
10) Implement a 'previous direction: ' do show where you last went?

# check if works: 

Bow damage


IDEA: 
Collecting runes (from totem maybe?), 3 runes in total? 
Crafting station to craft staffs
'''

import os # clearCOnsole
from colorama import Fore
import random as r
from zork_imports import bossnames, items, opposite_directions, upgradesToWeapons, biome_names, staff_names
import tkinter as tk
from tkinter import colorchooser
import math


# Global variables
current_path = []  # Keeps track of all paths already taken
max_bossHealth = 100
bossDealsDmg = 8
max_playerHealth = 100
player_health = 100  # Global variable, game over if drops to 0
available_items = ['Healing Potion']  # Stores your items, start with 1 
dmg_multiplier = 1 # damage mulitiplier, increases with increased dmg potion
luck_stat = 1 # luck stat, increases with luck potion
last_direction = ''
weaponUpgrades = {'Bleed'      : [3, False],   # 3 extra dmg per turn
                 'Extra Sharp' : [10, False], # 10 extra dmg permanent 
                 'Lethal Blade': [10, False], # 10% of instakill
                 'Stun Adapter': [20, False]} # 20% of paralyze 

runes = { 'Plain' : 5, 
          'Rare' : 5, 
          'Legendary' : 5 }

mage_staves = {} # mt dic contatining staffs {'Lightning staff' : ['Stun' : 10, 'Life Steal' : 5], ...}


coins = 20
poisoned = False
survivedCounter = 1 # how many steps you have survived
generatedTotems = {}
stringDamage = 0  # extra damage from strings found
totemsHeld = '' # key of the totem held
poisonMultiplier = 0 # 0 extra damage, +1 for every 5 steps in tierUp function
clairvoyance = False
previous_event = 3 # index of the last event, prevents same 2 in a row. 3 is default, and prevents bossEvent in the first step
held_item = {}

def main():
    global player_health, survivedCounter, poisonMultiplier, previous_event  # Access global variable
    print('\n=== Welcome to ZORG! === ')
    generateAllTotems()
    #showLoadout()    

    while player_health > 0:
        direction = valid_direction_input()
        current_path.append(direction)
        while(direction in ['u', 'p', 'h']):
            if(direction == 'u'):
                itemSelection()

            if(direction == 'p'):
                show_path_popup(current_path) # p shows the path

            if(direction == 'h'):
                healthbar(player_health, 'PLAYER')

            direction = valid_direction_input() # så lenge u, p, h skrives, spør om direction på nytt

        if not call_random_event():  # Check if the event was successfully conquered
            print(f"\n{Fore.RED}Game Over!{Fore.WHITE} You survived for {Fore.BLUE}{survivedCounter}{Fore.WHITE} steps")
            print(f'{Fore.YELLOW}Your path has been printed in a popup screen below{Fore.WHITE}')
            break
       
        if(poisoned == True): # if player has been poisoned, decreases health by 2 each turn he walks
            poisonDmg = 2 + poisonMultiplier
            print(f'{Fore.GREEN}Poison{Fore.WHITE} deals{Fore.RED} {poisonDmg} damage{Fore.WHITE}'.rjust(140))
            player_health -= poisonDmg
            if(player_health <= 0):
                print(f"\n{Fore.RED}Game Over!{Fore.WHITE} You survived for {Fore.BLUE}{survivedCounter}{Fore.WHITE} steps")
                print(f'{Fore.YELLOW}Your path has been printed in a popup screen below{Fore.WHITE}')
                break

        current_path.append(direction) # the user has typed a n,s,w,e direction
        survivedCounter += 1
        tierUp(survivedCounter) # increases the difficulty each 5 turns
    show_path_popup(current_path) # once game is over, prints popup window with path

        

class ColorGridApp:
    def __init__(self, root, path, grid_size=30):
        self.root = root
        self.path = path
        self.grid_size = grid_size
        self.cell_size = 40  # Size of each cell in pixels
        self.canvas = tk.Canvas(self.root, width=self.grid_size * self.cell_size, height=self.grid_size * self.cell_size)
        self.canvas.pack()
        self.create_grid()
        self.draw_path()

    def create_grid(self):
        for i in range(self.grid_size):
            # Horizontal lines
            self.canvas.create_line(0, i * self.cell_size, self.grid_size * self.cell_size, i * self.cell_size, fill="gray")
            # Vertical lines
            self.canvas.create_line(i * self.cell_size, 0, i * self.cell_size, self.grid_size * self.cell_size, fill="gray")

    def draw_path(self):
        middle = self.grid_size // 2
        row, col = middle, middle  # Start in the middle of the grid
        for direction in self.path:
            x1 = col * self.cell_size
            y1 = row * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="blue", outline="blue")
            if direction == 'n':
                row -= 1
            elif direction == 's':
                row += 1
            elif direction == 'e':
                col += 1
            elif direction == 'w':
                col -= 1

def totemMultiplier(a): 
    # takes the key, e.g., 'Bleed', 'Healing Potion', and returns the value in this format: 1.67 (67%)
    global totemsHeld, generatedTotems
    
    # Try to get the dictionary; if not found, use an empty dictionary
    totemDic = generatedTotems.get(totemsHeld, {})

    # Iterate over the dictionary's values
    for i in range(len(totemDic)):
        if totemDic[i][0] == a:
            multipl = float(totemDic[i][1] / 100) + 1
            return multipl  # returns value as 1.67 e.g.

    # If no matching key was found, return 1
    return 1
    
   



def generateAllTotems():
    # random amount of effect between 2-5, with random 
    # how to do this? 
    # the biomes should be easy
    # create several sets containing 2-5 lists, and append to each biome name

    # Initialize the dictionary    
    itemsNames = ['Healing Potion',      
         'Increased DMG Potion',
         'Luck Potion',
         'MAX Health Potion',
         'Overall Cost Reduction']

# Create the dictionary entries for the biomes with the desired structure
    setOfPerks = set()
    for i in range(len(biome_names)):
        # Create a tuple with a random number of lists, each containing some text
        num_lists = r.randint(1, 4)
        setOfPerks = tuple([itemsNames[r.randint(0, 4)], determinePercentage(10, 50)] for _ in range(num_lists))
        
        # Add the filled tuple to the dictionary
        generatedTotems[biome_names[i]] = setOfPerks

    #generatedTotems = {'adsadsa' : (['Lethal Blade', 20], ['Healing Potion', 50], []...), 
        #               {'Mystic Forest' : ([], [], [], [], [])}

def determinePercentage(min, max):
    # returns a random percentage in incremets of 5, between 10 and 50.
    multiples_of_five = [num for num in range(min, max + 1) if num % 10 == 0] # [10, 20, 30 ..]
    return multiples_of_five[r.randint(0, len(multiples_of_five)-1)]

def show_path_popup(path):
    root = tk.Tk()
    root.title("Player Path")
    app = ColorGridApp(root, path)
    root.mainloop()

def printUpgrades():
    global weaponUpgrades
    print(f'\n{Fore.BLUE}Upgrades currently on your weapon:{Fore.WHITE} ')
    print(f'{Fore.YELLOW}Bleed{Fore.WHITE} /// 3 dmg per turn' if weaponUpgrades['Bleed'][1] == True else None)
    print(f'{Fore.YELLOW}Extra Sharp{Fore.WHITE} /// + 10 dmg permanently ' if weaponUpgrades['Extra Sharp'][1] == True else None)
    print(f'{Fore.YELLOW}Lethal Blade{Fore.WHITE} /// 10% chance of instakill' if weaponUpgrades['Lethal Blade'][1] == True else None)
    print(f'{Fore.YELLOW}Stun Adapter{Fore.WHITE} /// 20% of paralyzing opponent' if weaponUpgrades['Stun Adapter'][1] == True else None)

def itemSelection():
    global available_items, weaponUpgrades # items you have boughtn
    printTotem()
    printUpgrades()
    printHeldItems()

    if(len(available_items) != 0): 
        itemSelectionScreen()
        choice = input("\nWhich item would you like to use? (q = quit) ").strip().lower()
        matches = find_item(choice, items)
    else: 
        print('You have no items!') # no items
        return  
    # now we want to use the item
    
#def checkIfPurchasedUpgrades():
  ##  return ()

    if matches:
        found = False
        for match in matches:
            if match in available_items:
                # here comes switch case logic
                usePotion(match) # 

def printHeldItems() -> None:
    global held_item
    if(held_item):
        key = next(iter(held_item))
    
        print(f'Staff held: {Fore.GREEN}{key}{Fore.WHITE}, granting {Fore.GREEN}{held_item[key]}{Fore.WHITE}\n')

def printTotem():
    global totemsHeld
    try: 
        short = generatedTotems[totemsHeld]
        print(f'\n{Fore.BLUE}{totemsHeld} Totem: {Fore.WHITE}', end='')
        # logic for printing
        for i in range(len(short)): # prints all the perks it has
            print(f'{Fore.GREEN}{short[i][0]}{Fore.WHITE} + {short[i][1]}%  ', end='') 
    except: print(f'{Fore.GREEN}NO TOTEMS{Fore.WHITE}')



def itemSelectionScreen():
    global available_items # items you have bought

    print('////////////////////////')
    print(f"{Fore.BLUE}You have the following items:{Fore.WHITE}")
    for i in range(len(available_items)):
        print(f'--- {Fore.GREEN}{available_items[i]}{Fore.WHITE} ---')
    print('////////////////////////')

def usePotion(potion):
    global player_health, dmg_multiplier, luck_stat, max_bossHealth, poisoned, max_playerHealth, clairvoyance # access global variable
    if potion == 'Healing Potion':
        health_gain = int(40 * totemMultiplier('Healing Potion'))
        player_health = min(player_health + health_gain, max_playerHealth)
        print(f'--- {Fore.GREEN}Your health has increased by {health_gain}!{Fore.WHITE} ---')
        healthbar(player_health, 'Player')
    elif potion == 'Increased DMG Potion':
        dmg_mulitplier_increase = 0.1 * totemMultiplier('Increased DMG Potion') # calcs the totem bonus
        dmg_multiplier += 0.1 * dmg_mulitplier_increase
        print(f'--- {Fore.GREEN}Your damage multiplier has increased by {dmg_mulitplier_increase}!{Fore.WHITE} ---')
    elif potion == 'Clairvoyance Potion':
        pass # shows you the path infront, or allows you 2 tries? fix fix fix
        clairvoyance = True # activated
        print(f'{Fore.YELLOW}\nYou can now reveal the next path you type in!{Fore.WHITE}\n')
    elif potion == 'Luck Potion':
        luck_increase = float(1.2 * totemMultiplier('Luck Potion'))
        luck_stat *= luck_increase # increases luck (amount of coins you get)
        print(f'---{Fore.GREEN}Your luck has increased by {luck_increase*10}%!{Fore.WHITE}---')
    elif potion == 'MAX Health Potion':
        max_bossHealth_decrease = int(10 * totemMultiplier('MAX Health Potion'))
        max_bossHealth -= max_bossHealth_decrease # decreases boss healht by 10
        print(f'---{Fore.GREEN}All boss\'s health has decreased by {max_bossHealth_decrease}!{Fore.WHITE}---')
    elif potion == 'Antidote':
        if(poisoned == True):
            print(f'You have been cured of the {Fore.GREEN}poison!{Fore.WHITE}')
            poisoned = False # cures you
        else: 
            print('You are not poisoned...') # not poisoned
            available_items.append(potion) # appends 1 potion, and then immediatly removes below. So stays unchanged
        

    available_items.remove(potion) # removes the potion you just used


def checkIfUpgraded(upgradeName):
    return (weaponUpgrades[upgradeName][1] == True) # returns true if it has been purchased

def trap():
    global player_health
    print(f'\n {Fore.RED} --- Ouch! {Fore.WHITE} You fall into a pitfall trap and lose some health ---')
    player_health -= 7
    healthbar(player_health, 'PLAYER')
    #return player_health > 0
    return player_health > 0

def gather_coins():
    global luck_stat
    print(f'\n--- You stumble upon a chest filled with {Fore.YELLOW} gold coins! {Fore.WHITE} ---')
    coinAmount(coins_aquired_rn=int(10*luck_stat))
    return True

def find_item(query, itemsOrUpgrades):
    query = query.lower()
    matched_items = [item for item in itemsOrUpgrades.keys() if query in item.lower()]
    return matched_items

def shopMenu(whichShopInventory):
        selected_items = set()  # Use a set to track selected items
        print('-' * 80)
        print(f'\t\t\t       ======= SHOP ======= \t\t\t {Fore.GREEN}{coins} COINS{Fore.WHITE}')
        reductionInCost = int(math.ceil(2 - totemMultiplier('Overall Cost Reduction')))

        for i in range(10):
            if i % 3 != 0:
                print('|' + ' ' * 78 + '|')
            else:
                # Ensure a new unique item is selected
                while True:
                    selected_item = list(whichShopInventory.keys())[r.randint(0, len(whichShopInventory) - 1)]
                    if selected_item not in selected_items:
                        break
                
                selected_value = float(whichShopInventory[selected_item] * reductionInCost)
                selected_items.add(selected_item)  # Add the item to the set
                print(f'\t\t\t  {Fore.BLUE} {selected_item} {Fore.WHITE} : {selected_value} coins')

        print('-' * 80)
        return selected_items

def specificShop(whichShop, whichList):
    global coins
    choice = ''  # Unassigned
    print('\n\n\t\t\t------ You stumble upon a shop! ------')
    list_of_items = shopMenu(whichShop)

    while coins > 0 and choice != 'q':
        choice = input("\nWhich item would you like to buy? (q = quit) ").strip().lower()
        if choice == 'q':
            break
        matches = find_item(choice, whichShop) # checks for 'entydig' navn på enten upgrades eller items
        
        if matches:
            found = False
            for match in matches:
                if match in list_of_items:
                    price = int(math.ceil(whichShop[match] * (2 - totemMultiplier('Overall Cost Reduction'))))# 2-1,34 = 0.66
                    if coins >= price:
                        coins -= price
                        print(f"\n🎉 You bought {Fore.GREEN} {match} {Fore.WHITE} for {Fore.YELLOW} {price} coins! {Fore.WHITE} 🎉")
                        list_of_items.remove(match)
                        # appends item to list, or makes upgrade to True
                        if whichShop == items:
                            whichList.append(match)
                        else: whichList[f'{match}'][1] = True # gjør om til KJØPT

                        found = True
                        break
                    else:
                        print(f"\n❗️ You don't have enough coins for {match}.")
                        found = True
                        break
            if not found:
                print("\n⚠️ The item you selected is not available in this shop.")
        else:
            print("\n🔍 No items matched your query.")
        
    if coins <= 0:
        print("\n💸 You have no more coins left! Visit again soon! 💸")
    
    return True

def coinAmount(coins_aquired_rn):
    global coins
    coins += coins_aquired_rn # increases global coins
    coin_bar = [''.join(f'{Fore.YELLOW}#{Fore.WHITE}' for _ in range(coins // 5))]
    coin_bar.append(''.join('-' for _ in range((100 - coins) // 5)))
    combined_coins_bar = ''.join(coin_bar)
    print(f'======  {Fore.YELLOW} +{10*luck_stat} Coins {Fore.WHITE}   ======')
    print(coins, ' COINS ', combined_coins_bar, '\n')

def tierUp(sc):
    global max_bossHealth, bossDealsDmg, poisonMultiplier
    if(sc % 5 == 0): # every 5 turns
        print(f"{Fore.RED}You have now passed {sc} steps, difficulty increases{Fore.WHITE}".rjust(140))
        max_bossHealth += 10 # 10 more health on average
        bossDealsDmg += 2 # deals 2 more damage to player
        poisonMultiplier += 1 # 1 more damage every 5 turns


def printMonster(a, b):
    
    # prints a 'monster', and the weakness of each body parts. (Fallout 4 VATS)
    
    # a = body_values
    # b = body_hit_percantages
    body_colors = {} # mt dictionary

    for part, value in a.items(): # creates dic connecting body part to color
        color = getColorValues(value)
        body_colors[part] = color
        afl = '\t\t\t\t\t\t\t\t\t' # adjust from left in whitespaces
    
    
    print(f"\n{afl}\t\t\t    Head {body_colors['Head']}{a['Head']}{Fore.WHITE}, {b['Head']}%\n\n")
    print(f"\t{afl}Left-Shoulder {body_colors['Left-Shoulder']}{a['Left-Shoulder']}{Fore.WHITE}, {b['Left-Shoulder']}%\t\t" 
          f"Right-Shoulder {body_colors['Right-Shoulder']}{a['Right-Shoulder']}{Fore.WHITE}, {b['Right-Shoulder']}%\n\n")
    print(f"{afl}\t\t\t   Torso {body_colors['Torso']}{a['Torso']}{Fore.WHITE}, {b['Torso']}%\n")
    print(f"\n{afl}\t\t\t   Waist {body_colors['Waist']}{a['Waist']}{Fore.WHITE}, {b['Waist']}%\n\n")
    print(f"\t{afl}Left-Leg {body_colors['Left-Leg']}{a['Left-Leg']}{Fore.WHITE}, {b['Left-Leg']}%\t\t\t"\
          f"  Right-Leg {body_colors['Right-Leg']}{a['Right-Leg']}{Fore.WHITE}, {b['Right-Leg']}%")



def showLoadout():
    print(f'\n{Fore.BLUE}Your current loadout is: {Fore.WHITE}', end="")
    printUpgrades()
    #printBowUpgrades()
    #printMageSpells()


def giantEvent():
    global player_health, stringDamage
    body_values = {'Head' : determinePercentage(10, 100),
                   'Right-Shoulder' : determinePercentage(10, 100), 
                   'Left-Shoulder' : determinePercentage(10, 100), 
                   'Torso' : determinePercentage(10, 100), 
                   'Waist' : determinePercentage(10, 100), 
                   'Right-Leg' : determinePercentage(10, 100), 
                   'Left-Leg' : determinePercentage(10, 100)} # updates for each attack
    
    body_hit_percentages = {'Head' : determinePercentage(70, 100),
                   'Right-Shoulder' : determinePercentage(70, 100), 
                   'Left-Shoulder' : determinePercentage(70, 100), 
                   'Torso' : determinePercentage(70, 100), 
                   'Waist' : determinePercentage(70, 100), 
                   'Right-Leg' : determinePercentage(70, 100), 
                   'Left-Leg' : determinePercentage(70, 100)}
    
    giantHealth = 100
    
    print(f' {Fore.RED}\n\t      ***** YOU SEE A GIANT APPROACH YOU *****{Fore.WHITE}')
    print(f' {Fore.BLUE}\n\t  //////////////// You equip your bow //////////////{Fore.WHITE}\n')

    while(giantHealth > 0 and player_health > 0): 
        miss = False
        printMonster(body_values, body_hit_percentages) # returns body values

        if(miss == False): 
            healthbar(giantHealth, 'Giant')
            healthbar(player_health, 'Player')

       
        choice = input(f"\nWhich limb to attack: (u = use items) {Fore.GREEN}{Fore.WHITE} ").strip().lower()
        while(choice == 'u'):
            itemSelection() #  allows use of items
            choice = input(f"\nWhich limb to attack:  {Fore.GREEN}{Fore.WHITE} ").strip().lower()

        matches = find_item(choice, body_values) # 
        matches = matches[0] # unpacks value, ['Waist'] ---> 'Waist'  

        if matches:
            limb = body_values[matches]   
            limb_percentage = body_hit_percentages[matches]

        if(body_hit_percentages[matches] > r.randint(0, 100)):
            dmgDealt = attackLimb(limb, bow_damage=30+stringDamage) # 30 + 5 for every string found
            giantHealth -= dmgDealt # damages the giant
            clearConsole()
            print(f'\nDealt {Fore.RED}{dmgDealt} dmg{Fore.WHITE} to the {Fore.BLUE}{matches}{Fore.WHITE}, with a {Fore.GREEN}{int(limb)}%{Fore.WHITE} multiplier!\n')
            body_values[matches], body_hit_percentages[matches] = updateLimbs(limb, limb_percentage) # updates the limbs after each attack
            body_values[matches] = int(body_values[matches])
        else: 
            clearConsole() # clears scrreen
            print(f'You missed the {Fore.RED}{matches}{Fore.WHITE}!\n')
            miss = True # prevents healthbar from being printed above
        
        if(giantHealth > 0): player_health -= int(bossDealsDmg * r.uniform(1, 1.5)) # only if still alive it can attack
            

    if(player_health <= 0):
        print(f'{Fore.RED}=== YOU DIED ==={Fore.WHITE}')
        return False
    
    print(f'\n===== {Fore.GREEN}You have defeated the giant{Fore.WHITE}======\n')

    return True  



def clearConsole():
    os.system('cls' if os.name == 'nt' else 'clear')

def updateLimbs(l, bhp):
    l *= 0.9 # 20% decrease in dmg?
    bhp -= 10 # 15 % increase in accuracy
    return l, bhp



def attackLimb(limb, bow_damage): # 'limb' is here = accuracy to hit the limb, ex 80 or 70
    return int(bow_damage * limb//100)


def getColorValues(val): 
    # returs the color
    fore_dic = {30 : Fore.RED, 50 : Fore.YELLOW, 70 : Fore.GREEN} # dic which dictates the color of the weaknesses
    sorted_keys = sorted(fore_dic.keys()) # [30, 50, 70]
    
    # Iterate through the sorted keys to find the appropriate color
    for threshold in sorted_keys:
        if val <= threshold:
            return fore_dic[threshold]
    
    # If the value exceeds the highest threshold, return the highest color
    return fore_dic[sorted_keys[-1]]


def itemShop():
    specificShop(items, available_items)
    return True

def upgradeShop():
    specificShop(upgradesToWeapons, weaponUpgrades)
    return True

def poisonedTripwire():
    global poisoned
    if(poisoned == True):
        print(f"\n🚨 You jump over the {Fore.GREEN}poison tripwire{Fore.WHITE} this time!")
        return True
    else: 
        # poisons the player, requires them to find an antidote
        print(f"\n🚨 You've triggered a {Fore.RED}poison trap!{Fore.WHITE} Find {Fore.GREEN}antidote{Fore.WHITE} in a shop!\n")
        poisoned = True
        return True

def call_random_event():
    global clairvoyance, previous_event
    # REFERENCE STORAGE, these are acutally functions, but only a reference. The actual functions gets called in the 'return'
    # List of event
    # implement last_selected_event logic
    all_events = [gather_coins, itemShop, trap, bossEvent, upgradeShop, poisonedTripwire, randomBiome, findString, craftingStation]
    weights = [10, 15, 15, 15, 15, 10, 15, 15, 5] #Corresponding weights for each event
    if(survivedCounter % 10 != 0):
        selected_event = r.choices(all_events, weights=weights, k=1)[0]  # Select a random event based on the specified weights
    else: 
        selected_event = giantEvent # every 10 turns, spawns a guaranteed giant event

    while(selected_event == previous_event):
        selected_event = r.choices(all_events, weights=weights, k=1)[0] # prevents same in a row!!
    previous_event = selected_event # update previous event

    if(clairvoyance == False):
        if(selected_event()):
            last_selected_event = selected_event # store event, so that it cant be repeated in next step
            return True
        else: return False
    else: 
        clairvoyance = False # resets value
        event_dic = {gather_coins : 'Coins', 
                     itemShop : 'an Item Shop', 
                     trap : 'a Trap', 
                     bossEvent : 'a Boss Fight', 
                     upgradeShop : 'an Upgrades Shop', 
                     poisonedTripwire : 'a Poisoned Tripwire', 
                     randomBiome : 'a Totem Biome'}
        print(f"\n{Fore.BLUE}You see {event_dic[selected_event]} ahead{Fore.WHITE} ")
        ans = input('Go this direction? (y/n)')
        while(ans != 'y' and ans != 'n'):
            ans = input('Go this direction? (y/n)')
        if(ans == 'y'):      
            if(selected_event()):
                last_selected_event = selected_event # store event, so that it cant be repeated in next step
            return True
        elif(ans == 'n'): 
             selected_event = r.choices(all_events, weights=weights, k=1)[0] 
             return True
            


def craftingStation() -> True:
    # put 10 runes into the staff. Each rune has a value rating, meaning more legendaries give a better staff!

    print(f'{Fore.CYAN}/// Create your own staff using 10 runes ///{Fore.WHITE}')

    runesUsed = 0
    runesLeftTill10 = 10
    valueOfRunesUsed = 0

    while runesUsed < 10:
        plain_runes = min(int(input(f'How many Plain runes: [{runesLeftTill10}] remaining: ')), runesLeftTill10)
        runesUsed += plain_runes
        runesLeftTill10 -= plain_runes
        valueOfRunesUsed += 1 * plain_runes # val= 1

        if runesUsed >= 10:
            break

        rare_runes = min(int(input(f'How many {Fore.BLUE}Rare runes:{Fore.WHITE} [{runesLeftTill10}] remaining: ')), runesLeftTill10)
        runesUsed += rare_runes
        runesLeftTill10 -= rare_runes
        valueOfRunesUsed += 2 * rare_runes # val=2


        if runesUsed >= 10:
            break

        legendary_runes = min(int(input(f'How many {Fore.YELLOW}Legendary runes:{Fore.WHITE} [{runesLeftTill10}] remaining: ')), runesLeftTill10)
        runesUsed += legendary_runes
        runesLeftTill10 -= legendary_runes
        valueOfRunesUsed += 3 * legendary_runes # val=3


        if runesUsed >= 10:
            break

    # Call createStaff with the total number of runes used
    createStaff(valueOfRunesUsed)
    return True


def createStaff(val) -> None: 
    global mage_staves

    available_enchants = ['Soul Drain', 'Burning Aura', 'Clairvoyance', 'Healing', 'Poison Immunity']
    # create staff, Each rune has a value rating, meaning more legendaries give a better staff!
    det_name = r.choice(staff_names)
    mage_staves[det_name] = r.choice(available_enchants)
    print(f'\n{Fore.BLUE}You created {det_name} - granting | {mage_staves[det_name]} | {Fore.WHITE}, {val} rune value')


    if(not held_item):
        held_item[det_name] = mage_staves[det_name] # no staff held yet
        #print(held_item)
    else: 
        print(f'You put the {det_name} into your inventory!') # already a staff held
    



def findString(): 
    # the player locates some string which upgrades the bow damage
    lostTreasure()
    return True

def lostTreasure():
    global stringDamage
    stringDamage += 5 # updates by 5 for every dmg
    print(f'{Fore.GREEN}You find some lost treasure!{Fore.WHITE}')
    print(f'- Some{Fore.GREEN} nylon {Fore.WHITE}string (+5 dmg to bow, now {Fore.RED}{30+stringDamage}{Fore.WHITE})')
    for _ in range(0, r.randint(0, 1)): # either 1 or 2 healing pots
        print(f'- {Fore.GREEN}Healing Potion {Fore.WHITE}')
        available_items.append('Healing Potion')


def  randomBiome():
    global totemsHeld
    # the player finds a randomly generated area, with some randomly generated items which give some random effects
    biome = biome_names[r.randint(0, len(biome_names)-1)] # random biome
    print(f'You have entered the {Fore.BLUE}{biome}{Fore.WHITE}')
    if(totemsHeld == ''): # if space for 1 totem
        displayTotemInfo(biome) # display the current biomes totem
        ans = input(f'Pick up the {biome} totem? (y/n): ')
        while(ans != 'y' and ans != 'n'):
            print('Invalid input!')
            ans = input(f'Pick up the {Fore.BLUE}{biome}{Fore.WHITE} totem? (y/n): ')
        
        if(ans == 'y'):
            print(f'\nYou picked up the {Fore.BLUE}{biome}{Fore.WHITE} Totem!')
            # add the totem to the player's held totems
            totemsHeld = biome
            return True
        else:
            return True
    else: 
        print('You see no totems, and simply walk along!')
        return True

    

def displayTotemInfo(biome):
    short = generatedTotems[biome]
    print(f"\n{'='*40}")  # Top border
    print(f"{Fore.BLUE}{biome} Totem{Fore.WHITE}".center(40))  # Centered title
    print(f"{'-'*40}")  # Separator line
    
    # Iterate through and print the perks
    for i in range(len(short)): 
        perk_name = f"{Fore.GREEN}{short[i][0]}{Fore.WHITE}"
        perk_value = f"{short[i][1]}%"
        print(f"{perk_name:<30}{perk_value:>10}")  # Left align perk name, right align value
    
    print(f"{'='*40}\n")  # Bottom border


          

def valid_direction_input():
    global last_direction
    direction = input(f"{'Choose a direction (N, S, W, E): ':>120}").strip().lower()
    while direction not in ['n', 's', 'w', 'e', 'u', 'p', 'h'] or direction == last_direction: # bare retninger og u, og ikke gå tilbake
        direction = input('INVALID, enter direction (N, S, W, E): ').strip().lower()
    clearConsole()
    if(direction != 'u' and direction != 'p' and direction != 'h'): # u and p and h are exceptions
        last_direction =  opposite_directions[direction] # saves direction, uses dic to determine that if 'n', you cant 's' after
    return direction

def swordAttack(bh, par):
    if r.randint(1, 10) < 8:
        #damage = r.randint(15, 30)
        damage = calculatedDamage(15, 30)
        bh -= damage  # Success
        print(f"\nSword attack {Fore.GREEN}succeeded{Fore.WHITE}, dealt {Fore.RED}{damage}{Fore.WHITE} damage")
        if(checkIfUpgraded('Bleed')): # if bleed been purchased
            bh -= 3 # bleeds for 3 dmg
            print(f"{Fore.RED}Boss bled for 3 dmg{Fore.WHITE}")
        if(checkIfUpgraded('Lethal Blade')):
            if(r.randint(1,10) <= 1): # 10% chance
                bh -= bh # ex 47 - 47 = 0 
                print(f'{Fore.LIGHTMAGENTA_EX}\t/// INSTA-KILL ///{Fore.WHITE}')
        if(checkIfUpgraded('Stun Adapter')):
            if(r.randint(1,10) <= 5): # 20% chance
                par = True
                print(f'Boss is {Fore.YELLOW}paralyzed{Fore.WHITE} for 1 turn')

    else:
        print(f"\nSword attack {Fore.RED} missed {Fore.WHITE}")
    return bh, par

def magicAttack(bh):
    if r.randint(1, 10) < 5:  # 50% chance of success
        damage = calculatedDamage(40, 60)
        bh -= damage
        print(f"\nMagic attack {Fore.GREEN}succeeded{Fore.WHITE}, dealt {damage} damage")
    else:
        print(f"\n___ Magic attack {Fore.RED} missed {Fore.WHITE} ___")
    return bh

def bowAttack(bh):
    global stringDamage 
    if r.randint(1, 10) < 8:  # 80% chance of success
        damage =  30+stringDamage # 30 + 5 for each nylon string collected
        bh -= damage
        print(f"\nBow attack {Fore.GREEN}succeeded{Fore.WHITE}, dealt {damage} damage")
    else:
        print(f"\n___ Bow attack {Fore.RED} missed {Fore.WHITE} ___")
    return bh

def calculatedDamage(a, b):
    exSharp = 0
    if checkIfUpgraded('Extra Sharp'): # if has been purchased (== True)
        exSharp = weaponUpgrades['Extra Sharp'][0]
    dmg = int((r.randint(a, b)) * dmg_multiplier) + exSharp # fx: 16*1.1 = 17.6 = 17 int
    return dmg

def bossEvent(): 
    global player_health  # Update player_health
    paralyzed = False # initialize paralyze as 0

    boss_name = r.choice(bossnames)
    bossHealth = r.randint(max_bossHealth//2, max_bossHealth)
    difficultyIndex = bossHealth  # for calculating rune drops later on in 'bossDrops'
    print(f'\n{Fore.RED}{boss_name}{Fore.WHITE} has appeared!')
    healthbar(bossHealth, 'BOSS')
    # Boss battle
    while bossHealth > 0:
        if player_health > 0:
            
            choice = input("Choose your attack: ('s'word, 'm'agic, 'b'ow and arrow): ").strip().lower()
            while (choice != 's' and choice != 'm' and choice != 'b'):
                choice = input("Choose your attack: ('s'word, 'm'agic, 'b'ow and arrow): ").strip().lower()
            clearConsole()
            if choice == 's':
                bossHealth, paralyzed = swordAttack(bossHealth, paralyzed)
            elif choice == 'm':
                bossHealth = magicAttack(bossHealth)
            elif choice == 'b':
                bossHealth = bowAttack(bossHealth)
            else:
                print("Invalid choice. Please select 's', 'm', or 'b'.")
                continue  # Skip the rest of the loop for invalid input

        else: return False

        if(paralyzed == False and bossHealth > 0): # not paralyzed, and alive
            dmgDealtByBoss = int(bossDealsDmg * r.uniform(0.8, 1.2))
            player_health -= dmgDealtByBoss  # Boss attacks back, UNLESS PARALYZED
            difficultyIndex += dmgDealtByBoss # updates difficulty, if the end result is a high value, means the boss had much health and did a lot of damage
        paralyzed = False # reset paralyze 
        healthbar(bossHealth, 'BOSS')  # Boss healthbar
        healthbar(player_health, 'PLAYER')  # Player healthbar

    print(f'\n//////////// {Fore.YELLOW}You have defeated the {boss_name}!{Fore.WHITE} ////////////\n')
    howHard = determineDifficulty(difficultyIndex)
    print(f"Difficulty index: {Fore.RED}{difficultyIndex} ({howHard}){Fore.WHITE}")
    bossDrops(difficultyIndex)

    return player_health > 0

def determineDifficulty(di) -> str:
    # returns the difficulty 'hard', ''normal, 'easy', based on the difficultyIndex
    if di <= 90: # easy difficulty
        return 'Easy'
    
    elif di <= 130: # medium difficulty
        return 'Medium'
    
    else: return 'Hard' # hard difficulty (most rewarded) 

def bossDrops(di) -> None:
    global runes
    # drops some random runes after defeat
    runes_that_can_be_dropped = ['Plain', 'Rare', 'Legendary']
    weights = [10, 5, 2] #Corresponding weights for each event

    dropped_runes = [r.choices(runes_that_can_be_dropped, weights=weights, k=1)[0] for _ in range(qualityOfBossFight(di))]
    for rune in dropped_runes:
        runes[rune] += 1
    print(f"{Fore.BLUE}Obtained:{Fore.WHITE} Plain runes[{runes['Plain']}]"
          f", {Fore.BLUE}Rare runes[{runes['Rare']}]{Fore.WHITE}"
          f", {Fore.YELLOW}Legendary runes[{runes['Legendary']}]{Fore.WHITE}")
    

    

def qualityOfBossFight(di) -> int:
    # returns the number of runes dropped based on the difficulty of the boss fight
    if di <= 90: # easy difficulty
        return 5
    
    elif di <= 130: # medium difficulty
        return 10
    
    else: return 15 # hard difficulty (most rewarded)
        
    

def healthbar(health, whom):  # Visible healthbar for both player and boss
    health_bar = [''.join(f'{Fore.GREEN}#{Fore.WHITE}' for _ in range(health // 5))]
    health_bar.append(''.join('-' for _ in range((100 - health) // 5)))
    combined_health_bar = ''.join(health_bar)
    print(f'\n{Fore.BLUE}{whom}{Fore.WHITE}: {health} HEALTH REMAINING {combined_health_bar}')

if __name__ == '__main__':
    main()

