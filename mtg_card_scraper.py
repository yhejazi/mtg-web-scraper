# import pyodbc
import requests as r
from bs4 import BeautifulSoup as bs
import re
from math import ceil
import numpy as np
import pandas as pd

def convertSymbol(imgAlt):
    ''' 
    Coverts a card symbol image to its corresponding text -
    Black = B, Blue = U, Red = R, Green = G, White = W, Variable Colorless = X, Colorless = C, Phyrexian Red = P, Tap = Tap, 
    E = Energy
    '''   
    if (imgAlt == "Variable Colorless"):
        return('X')
    elif (imgAlt == "Blue"):
        return('U')
    elif (imgAlt == "Tap"):
        return('Tap')
    elif (imgAlt.isnumeric()): # number can be multiple digits
        return(imgAlt)
    return(imgAlt[0])

def getSuperType(cardType, superType):
    ''' '''
    if any(supertype in cardType for supertype in supertypes):
        typeSplit = cardType.split()
        superType = (superType + ' ' + typeSplit[0]).strip()
        cardType = ' '.join(typeSplit[1:])
        # check again, there could be two supertypes
        if any(supertype in cardType for supertype in supertypes):
            typeSplit = cardType.split()
            superType = (superType + ' ' + typeSplit[0]).strip()
            cardType = ' '.join(typeSplit[1:])
    return(cardType, superType)


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
            if re.search(r'.+?(?=\s+—)', cardType):
                # if there is power/toughness or loyalty...
                if re.search(r'(?<=\().+?(?=\))', cardType):
                    typeNum = re.search(r'(?<=\().+?(?=\))', cardType)[0]

                subType = re.search(r'(?<=—\s)([^\\]+)', cardType)[0]
                cardType = re.search(r'.+?(?=\s+—)', cardType)[0]
                

            # Divide type~supertype
            supertypes = ['Basic', 'Host', 'Legendary', 'Ongoing', 'Snow', 'Tribal', 'World']
            superType = ''
            cardType, superType = getSuperType(cardType, superType)

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
            setAndRarity = card.findNext("td", {"class": "setVersions"}).find('img', alt=True)
            cardSet = re.search(r'^.+?(?=\s\()', setAndRarity['alt'])[0]
            rarity = re.search(r'(?<=\().+?(?=\))', setAndRarity['alt'])[0]

            # If the card has other sets (reprints)...
            if (card.findNext("div", {"class": "otherSetSection"})):
                otherSets = card.findNext("div", {"class": "otherSetSection"}).findAll('img', alt=True)
                # append reprints to cardlist as their own row
                for extraSet in otherSets:
                    extraCardSet = re.search(r'^.+?(?=\s\()', extraSet['alt'])[0]
                    extraRarity = re.search(r'(?<=\().+?(?=\))', extraSet['alt'])[0]
                    cardlist.append([cardTitle, superType, cardType, subType, typeNum, manaCost, convertedMana, extraCardSet, extraRarity, rules])

            cardlist.append([cardTitle, superType, cardType, subType, typeNum, manaCost, convertedMana, cardSet, rarity, rules])


    
    columnNames = ['cardName', 'superType', 'cardType', 'subType', 'typeNum', 'manaCost', 'convertedMana', 'cardSet', 'rarity', 'rules']
    df = pd.DataFrame(cardlist, columns=columnNames)

    df.to_csv(path_or_buf='output.csv', index = False)



    ##### Upload data to sql database #####

    # print("Connecting to database")
    # mydb = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER=is-info430.ischool.uw.edu;DATABASE=Lab2;UID=INFO430;PWD=wubalubadubdub')
    # print("Done connecting")
    # cursor = mydb.cursor()
    
    # # insert data into our database
    # insertCard = """
    # SET NOCOUNT ON; 
    # EXECUTE [INFO430].[insert_yhejazi]
    # @cardName = ?, 
    # @cardType = ?,
    # @mana = ?,
    # @convertedMana = ?,
    # @cardSet = ?,
    # @rarity = ?,
    # @rules = ?
    # """

    # print("Starting import...")

    # for card in cardlist:
    #     cursor.execute(insertCard, card)
    
    # #commit your transaction when finished
    # cursor.commit()
    # #close the connection and cursor
    # cursor.close()
    # mydb.close()

    # print("Import completed.")