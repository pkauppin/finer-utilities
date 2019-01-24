#! /usr/bin/env python3

# List all matched entities in a given category in their base forms and output them in order of appearance.
# The lemmatization requires that lemma forms and morphological tags be found in the input file.

from sys import stdin, stdout, stderr, argv
import re

argv.append('')

max_depth = 4
TAG = argv[1]
    
# Lemma forms that are usually in plural by default
pluralia = [
    'olympialaiset',
    'markkinat',
    'yhdysvallat',
    'uutiset',
    'voimat',
    'jokerit',
    'maat',
    'saaret',
    'vuoret',
    'laiset',
    'läiset',
    ]

# Plural forms of common pluralized elements
pl_forms = {
    'vuori'      : 'vuoret',
    'saari'      : 'saaret',
    'maa'        : 'maat',
    'voima'      : 'voimat',
    'sanoma'     : 'sanomat',
    'putous'     : 'putoukset',
    'kilpailu'   : 'kilpailut',
    'kisa'       : 'kisat',
    'aatti'      : 'aatit',
    'uutinen'    : 'uutiset',
    'markkina'   : 'markkinat',
    'festivaali' : 'festivaalit',
    'festari'    : 'festarit',
    'juhla'      : 'juhlat',
    'alppi'      : 'alpit',
    'viikko'     : 'viikot',
    'amerikka'   : 'amerikat',
    'vihreä'     : 'vihreät',
    'filippiini' : 'filippiinit',
    'yhdistynyt' : 'yhdistyneet',
    'inen'       : 'iset',
    'kunta'      : 'kunnat', 
    }

pl_regex = '.*(' + '|'.join(pluralia) + ')'

def partitive(lemma):
    if len(lemma) < 3:
        return lemma
    elif re.search('[aou]', lemma[-5:]):
        return lemma + '[a]'
    return lemma + '[ä]'


# Check morhological analyses for agreement in NUM and CASE
def congr(morph1, morph2):
    tags1 = re.findall('(CASE|NUM)=[A-Z]+', morph1)
    tags2 = re.findall('(CASE|NUM)=[A-Z]+', morph2)
    return tags1 == tags2

# return lemma (and possible plural marker) for word
def get_lemma(wform, lemma, morph, tag=''):

    if re.search('POS=NOUN|POS=NUMERAL|POS=ADJECTIVE|SUBCAT=QUANTOR', morph):
        if '[NUM=PL]' in morph and not re.fullmatch(pl_regex, lemma) and re.search('Enamex(Loc|Evt|Org)', tag):
            for sg, pl in pl_forms.items():
                if lemma.endswith(sg):
                    return (lemma+'#').replace(sg+'#', pl)
            return lemma + '[t]'
        return lemma
    return wform.lower()


def parse_numex(entity, tag='Numex'):

    unit = entity.pop()
    normalized = [ lemma for wform, lemma, morph in entity ]

    wform, lemma, morph = unit
    
    if ':' in wform or re.search('[A-Z]', wform):
        normalized.append(re.sub(':.+', '', wform))
        
    elif normalized == ['yksi'] or normalized == ['1']:
        normalized.append(lemma)
    
    else:
        normalized.append(partitive(lemma))
        
    return ' '.join(normalized)

    
# Expressions of time such as dates are parsed differently
def parse_timex(entity, tag='Timex'):

    normalized = []

    while len(entity) > 0:

        wform, lemma, morph = entity.pop()
        wform = wform.lower()
        
        if wform.endswith('kuuta') and len(entity) > 0:
            wform2, lemma2, morph2 = entity.pop()
            if 'SUBCAT=ORD' in morph2:
                normalized += [ wform ]
            else:
                normalized += [ lemma ]
            wform, lemma, morph = wform2, lemma2, morph2

        if wform in ['aikana', 'välillä', 'aikaa']:
            normalized += [ wform ] + [ e[0] for e in entity ][::-1]
            normalized = normalized[::-1]
            return ' '.join(normalized)

        if 'SUBCAT=ORD'in morph:
            normalized += [ lemma ]
            if len(entity) > 0:
                wform, lemma, morph = entity.pop()
                if wform.endswith('kuun'):
                    normalized += [ wform ]
                else:
                    normalized += [ lemma ]
        elif re.fullmatch('[0-9]+[.]?', wform):
            normalized += [ wform ]

        elif wform in ['vuonna', 'vuosina']:
            normalized += [ wform ]

        elif re.fullmatch('vuosi|.+kuu|päivä', lemma):
            normalized += [ lemma ]

        else:
            normalized += [ wform ]
    
    normalized = normalized[::-1]
    return ' '.join(normalized)


def parse_enamex(entity, tag='Enamex'):
    
    normalized = []
    
    wform, lemma, morph = entity.pop()
    if re.fullmatch('(18|19|20)[0-9][0-9]', wform) and tag.startswith('EnamexEvt') and len(entity) > 0:
        normalized += [ wform.lower() ]
        ( wform, lemma, morph ) = entity.pop()

    normalized += [ get_lemma(wform, lemma, morph, tag) ]
    while len(entity) > 0 and wform[0] != '-':
        morph0 = morph
        wform, lemma, morph = entity.pop()
        if re.search('POS=ADJECTIVE|SUBCAT=ORD|SUBCAT=QUANTOR', morph) and congr(morph, morph0):
            normalized += [ get_lemma(wform, lemma, morph, tag) ]
        else:
            normalized += [ wform.lower() ]
            break
    
    normalized = [ wform.lower() for wform, lemma, morph in entity ] + normalized[::-1]
    return ' '.join(normalized)



tag_columns = [ [], [], [], [] ]
analyses = []

for n, line in enumerate(stdin):
    
    line = line.rstrip(' \n')
    line = line.lstrip(' \t')
    
    if line != '':
        
        if '\t[POS=' not in line:
            stderr.write('WARNING: Line %i: Irregular morphological labels detected!\n' % n)
        try:
            fields = line.split('\t')
            wform, lemma, morph, semtag = fields[0:4]
            nertags = fields[4:]
        except:
            stderr.write('WARNING: Line %i: unexpected number of fields!\n' % n)
            exit(1)
        
        analyses.append(( wform, lemma, morph, semtag, n ))
        
        while len(nertags) < max_depth:
            nertags.append('')
        nertags = nertags[0:max_depth]
        
        for nertag, tag_column in zip(nertags, tag_columns):
            tag_column.append(nertag)
    
    else:

        tag_columns = tag_columns[0:max_depth]
        
        entities = []
        
        for tag_column in tag_columns:
            
            tag    = '#'
            tuples = []
            
            for ( wform, lemma, morph, semtag, i ), nertag in zip(analyses, tag_column):
                
                if nertag.startswith('<'+TAG) and not nertag.startswith('</'):
                    i0  = i
                    tag = nertag.strip('<>/')
                    tuples.append(( wform, lemma.lower(), morph, ))
                elif tuples != []:
                    tuples.append(( wform, lemma.lower(), morph, ))
                    
                cond1 = nertag.startswith('</'+tag)
                cond2 = nertag.startswith('<'+tag) and nertag.endswith('/>')
                
                if cond1 or cond2:
                    if tag.startswith('Enamex'):
                        ent_str = parse_enamex(tuples, tag)
                    elif tag.startswith('Timex'):
                        ent_str = parse_timex(tuples, tag)
                    elif tag.startswith('Numex'):
                        ent_str = parse_numex(tuples, tag)
                    else:
                        ent_str = ' '.join([ t[0] for t in tuples ])
                    entities.append(( i0, i, ent_str, tag, ))
                    tag    = '#'
                    tuples = []
        
        entities.sort()
        for i1, i2, ent_str, tag in entities:
            print('%i,%i\t%s\t%s' % ( i1, i2, ent_str, tag ))

        tag_columns = [ [], [], [], [] ]
        analyses = []
