# Magic: The Gathering Web Scraper

This is a web scraper that collects data of all Magic: The Gathering cards on Wizards of the Coast's [Gatherer website](https://gatherer.wizards.com/Pages/Search/Default.aspx?page=0&color=|[W]|[U]|[B]|[R]|[G])

## About the data
The Gatherer website is a database of every Magic: The Gathering card, including test cards. I scraped the data to include the following variables:
- **cardName**: The card name; string
- **superType**: The supertypes of a card (i.e. Legendary); string
- **cardType**: The types of a card (i.e. Creature); string
- **subType**: The subtype of a card (i.e. Equipment); string
- **typeNum**: The power/toughness or loyalty of a card if applicable; string
- **manaCost**: The mana cost of a card. Symbols converted using color code; string
- **convertedMana**: The converted mana cost of a card; float
- **cardSet**: The set of a card; string
- **rarity**: The rarity of a card; string
- **rules**: The rules (text) of a card. Symbols converted using color code; string

## To do
Things to be done:
- Mana cost images -> handle colorless mana numbers that are double digits
- Clean up rules escape characters, i.e. \’
- Clean up extra ‘ -‘ in subType
- Handle cards with more than 1 superType
- Handle superType edge cases (most fall in test cards)
- Check cardName for cards that has 2 names, or are a front + back card

