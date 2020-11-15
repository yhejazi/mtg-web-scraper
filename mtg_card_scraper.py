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

        print("Scraping page {0}/{1}".format(pageNum + 1, totalPages))

        for card in cardItem:
            cardName = card.findNext("span", {"class": "cardTitle"}).text.strip()   

            cardType = card.findNext("span", {"class": "typeLine"}).text.strip()
            m = re.search(r'([\w ]+)[\s—]*([\w ]+)?[\s]*(?:\(([\d\*/]+)\))?', cardType)
            if m:
                cardType, subType, typeNum = m.group(1).strip(), m.group(2), m.group(3)         

            # Divide type~supertype
            cardType, superType = getSuperType(cardType, '')

            convertedMana = card.findNext("span", {"class": "convertedManaCost"}).text.strip()

            # Get and format card rules
            rules = card.findNext("div", {"class": "rulesText"}).findAll("p")          
            rules = formatRules(rules)

            # Get abbreviated mana string
            manaCostImgs = card.findNext("span", {"class": "manaCost"}).findAll('img', alt=True)
            manaCostList = []
            for cost in manaCostImgs:
                manaCostList.append(convertSymbol(cost['alt']))
            manaCost = ''.join(manaCostList)

            # Get card set and rarity from right column
            setAndRarity = card.findNext("td", {"class": "setVersions"}).find('img', alt=True)['alt']
            cardSet, rarity = splitSetAndRarity(setAndRarity)


            # If the card has other sets (reprints)...
            if (card.findChild("div", {"class": "otherSetSection"})):
                otherSets = card.findChild("div", {"class": "otherSetSection"}).findAll('img', alt=True)
                # ...append reprints to cardlist as their own row
                for extraSet in otherSets:
                    extraCardSet, extraRarity = splitSetAndRarity(extraSet['alt'])
                    cardlist.append([cardName, superType, cardType, subType, typeNum, manaCost, convertedMana, extraCardSet, extraRarity, rules])


            cardlist.append([cardName, superType, cardType, subType, typeNum, manaCost, convertedMana, cardSet, rarity, rules])


    columnNames = ['cardName', 'superType', 'cardType', 'subType', 'typeNum', 'manaCost', 'convertedMana', 'cardSet', 'rarity', 'rules']
    df = cleanUp(pd.DataFrame(cardlist, columns=columnNames))

    df.to_csv(path_or_buf='data/output.csv', index = False)