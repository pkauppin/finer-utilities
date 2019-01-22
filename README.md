# finer-utilities

Various tools for processing [FiNER](https://github.com/Traubert/FiNer-rules/blob/master/finer-readme.md) (Finnish Named-Entity Recognizer) output.

## linearize.sh

Converts tagged standard input back into running text. Empty lines i.e paragraph breaks are inserted after certain closing tags such as `</paragraph>`, `</h1>` etc. 

## make-html.py

Linearizes standard input and outputs HTML with matched entities highlighted and color-coded.
The color codes are roughly as follows:
- **blue**: locations (`EnamexLoc___`)
- **red**: persons & beings (`EnamexPrs___`, excluding titles)
- **green**: orgainzations (`EnamexOrg___`)
- **purple**: products (`EnamexPro___`)
- **dark gray**: events (`EnamexEvt___`)
- **light gray**: numerical expressions (`NumexMsr___`)
- **yellow**: temporal expressions (`TimexTme___`)

## get-tags.sh

Lists all unique NE tags found in a tagged input file.

## lemmatize-matches.py

Reads standard input lists all matched entitiees in a given category in their base forms and print them in order of appearance. The input should contain lemma forms and morphological tags.

## lemmatized-freqs.sh

Reads standard input and creates a frequency list of all matched entities in a given category or subcategory. The names are listed in their normalized base forms along with their frequencies.

## freq-lists.sh

Creates frequency lists for all categories whose tags are found in the input file.