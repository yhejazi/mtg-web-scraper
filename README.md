# Magic: The Gathering Web Scraper

This is a web scraper that collects data of all Magic: The Gathering cards on Wizards of the Coast's [Gatherer website](https://gatherer.wizards.com/Pages/Search/Default.aspx?page=0&color=|[W]|[U]|[B]|[R]|[G])

## About the data
The Gatherer website is a database of every Magic: The Gathering card, including test cards. I scraped the data to include the following variables:
- **cardName**: The card name; string
- **superType**: The supertypes of a card; string

Supertypes: 'Basic', 'Host', 'Legendary', 'Ongoing', 'Snow', 'Tribal', 'World'
- **cardType**: The types of a card (i.e. Creature); string
- **subType**: The subtype of a card (i.e. Equipment); string
- **typeNum**: The power/toughness or loyalty of a card if applicable; string
- **manaCost**: The mana cost of a card. Symbols converted using color code; string

Black = B, Blue = U, Red = R, Green = G, White = W, Variable Colorless = X, Colorless = C, Phyrexian Red = P, Tap = Tap, E = Energy
- **convertedMana**: The converted mana cost of a card; float
- **cardSet**: The set of a card; string
- **rarity**: The rarity of a card; string

'Common', 'Uncommon', 'Rare', 'Mythic Rare', 'Special', 'Promo'
- **rules**: The rules (text) of a card. Symbols converted using color code; string

