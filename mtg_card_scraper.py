import requests as r
from bs4 import BeautifulSoup as bs
import re
from math import ceil
import numpy as np
import pandas as pd
from helper import *


if __name__ == '__main__':
    # Determine total number of pages
    page = r.get("https://gatherer.wizards.com/Pages/Search/Default.aspx?page=0&name=+[%22%22]")
    soup = bs(page.content, 'html.parser')
    termDisplay = soup.find("p", attrs={"class": "termdisplay"}).text.strip()
    totalCards = re.search(r'(\d+)', termDisplay).group()
    totalPages = ceil(int(totalCards) / 100)

    print("Total pages to scrape: ", totalPages)

    cardlist = []

    for pageNum in range(totalPages):
        page = r.get("https://gatherer.wizards.com/Pages/Search/Default.aspx?page={0}&name=+[%22%22]".format(pageNum))
        soup = bs(page.content, 'html.parser')
        cardItem = soup("tr", attrs={"class": "cardItem"})

        print("Scraping page {0}".format(pageNum))

        for card in cardItem:
            cardTitle = card.findNext("span", {"class": "cardTitle"}).text.strip()
            
            cardType = card.findNext("span", {"class": "typeLine"}).text.strip()
            # Divide type~subtype
            subType = 'NA' #np.NaN
            typeNum = 'NA'
            # If there is a dash (subtype)
            typeSplit = cardType.split('—')
            cardType = typeSplit[0].strip()

            if len(typeSplit) > 1:
                subTypeSplit = typeSplit[-1].split('(')
                subType = subTypeSplit[0].strip()
                # if there is power/toughness or loyalty...
                if len(subTypeSplit) > 1:
                    typeNum = subTypeSplit[-1].strip(') ')
                

            # Divide type~supertype
            supertypes = ['Basic', 'Host', 'Legendary', 'Ongoing', 'Snow', 'Tribal', 'World']
            superType = ''
            cardType, superType = getSuperType(cardType, superType, supertypes)
            cardType, superType = getSuperType(cardType, superType, supertypes) # check again, can have 2 supertypes

            convertedMana = card.findNext("span", {"class": "convertedManaCost"}).text.strip()

            # Get and format card rules
            rules = card.findNext("div", {"class": "rulesText"}).findAll("p")          
            for p in rules:
                # Convert rule symbols to text
                for image in p.findAll("img"):
                    convertedAlt = convertSymbol(image['alt'])
                    image.replaceWith(convertedAlt)
                index = rules.index(p)
                rules[index] = p.text.strip()  
            rules = "\n".join(rules)      

            # Get abbreviated string of mana cost
            manaCostImgs = card.findNext("span", {"class": "manaCost"}).findAll('img', alt=True)
            manaCostList = []
            for cost in manaCostImgs:
                manaCostList.append(convertSymbol(cost['alt']))
            manaCost = ''.join(manaCostList)

            # Get card set and rarity from right column
            setAndRarity = card.findNext("td", {"class": "setVersions"}).find('img', alt=True)['alt']
            cardSet, rarity = splitSetAndRarity(setAndRarity)


            ###### If the card has other sets (reprints)... ######
            if (card.findChild("div", {"class": "otherSetSection"})):
                otherSets = card.findChild("div", {"class": "otherSetSection"}).findAll('img', alt=True)
                # append reprints to cardlist as their own row
                for extraSet in otherSets:
                    extraCardSet, extraRarity = splitSetAndRarity(extraSet['alt'])
                    cardlist.append([cardTitle, superType, cardType, subType, typeNum, manaCost, convertedMana, extraCardSet, extraRarity, rules])
            ###### End of extra sets ######

            cardlist.append([cardTitle, superType, cardType, subType, typeNum, manaCost, convertedMana, cardSet, rarity, rules])


    
    columnNames = ['cardName', 'superType', 'cardType', 'subType', 'typeNum', 'manaCost', 'convertedMana', 'cardSet', 'rarity', 'rules']
    df = pd.DataFrame(cardlist, columns=columnNames)

    df.to_csv(path_or_buf='data/output.csv', index = False)