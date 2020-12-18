def cleanUp(df):
    '''
    Minor cleaning on the dataset, handling edge cases/test card anomalies
    '''
    df['rarity'] = df['rarity'].replace(['Land'],'Common')
    df['cardType'] = df['cardType'].replace(['instant', 'Elemental Instant'],'Instant')
    df['cardType'] = df['cardType'].replace(['Eaturecray', 'Scariest Creature You', 'Summon', 'Summon Wolf'],'Creature')
    df['subType'] = df['subType'].replace(['Igpay'],'Pig')
    df = df[~df.cardType.str.contains("Token", na=False)]
    df = df[~df.manaCost.str.contains("H", na=False)] # remove cards with half mana cost
    return df

def convertSymbol(imgAlt):
    ''' 
    Coverts a card symbol image to its corresponding text -
    Black = B, Blue = U, Red = R, Green = G, White = W, Variable Colorless = X, Colorless = C, Phyrexian Red = P, Tap = Tap, 
    E = Energy, H = Half
    '''
    imgAltWords = imgAlt.strip().split()
    if (len(imgAltWords) > 1):
        if (imgAlt == "Variable Colorless"):
            return('X')
        if ("Phyrexian" in imgAlt): 
            return('P')
        if ("Half" in imgAlt): 
            return('H')
        if ("or" in imgAlt and len(imgAltWords) > 2): # Double mana
            return(convertSymbol(imgAltWords[0]) + "|" + convertSymbol(imgAltWords[2]))
        else: # Oh oh :(
            raise Exception('Could not parse symbol:{}'.format(imgAlt))
    elif (imgAlt == "Blue"):
        return('U')
    elif (imgAlt == "Tap"):
        return('Tap')
    elif (imgAlt.isnumeric()): # number can be multiple digits
        return(imgAlt)
    return(imgAlt[0])

def formatRules(rules):
    '''
    Clean up, reformat images, and merge list of rule <p> tags; return string of rules
    '''
    for p in rules:
        # Convert rule symbols to text
        for image in p.findAll("img"):
            convertedAlt = convertSymbol(image['alt'])
            image.replaceWith(convertedAlt)
        index = rules.index(p)
        rules[index] = p.text.strip()  
    return("\n".join(rules))

def getSuperType(cardType, superType):
    supertypes = ['Basic', 'Host', 'Legendary', 'Ongoing', 'Snow', 'World']
    if any(supertype in cardType for supertype in supertypes):
        typeSplit = cardType.split()
        superType = (superType + ' ' + typeSplit[0]).strip()
        cardType = ' '.join(typeSplit[1:])
        cardType, superType = getSuperType(cardType, superType)
    return cardType, superType

def splitSetAndRarity(setAndRarity):
    '''
    Splits and returns separate set and rarity strings
    '''
    srSplit = setAndRarity.split("(")
    cardSet = srSplit[0].strip()
    rarity = srSplit[-1].strip(') ')
    return cardSet, rarity