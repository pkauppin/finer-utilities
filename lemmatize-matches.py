#! /usr/bin/env python3

# List all matched entities in a given category in their base forms and output them in order of appearance.
# The lemmatization requires that lemma forms and morphological tags be found in the input file.

from sys import stdin, stdout, stderr, argv
import re
import argparse

# FiNER entity tag prefixes
numex_pfx = 'Numex'
enamex_pfx = 'Enamex'
timex_pfx = 'Timex'

# Maximum number of entity levels considered (1 = no nested entities)
max_depth = 4
    
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
    'vuori': 'vuoret',
    'saari': 'saaret',
    'maa': 'maat',
    'voima': 'voimat',
    'sanoma': 'sanomat',
    'putous': 'putoukset',
    'kilpailu': 'kilpailut',
    'kisa': 'kisat',
    'aatti': 'aatit',
    'uutinen': 'uutiset',
    'markkina': 'markkinat',
    'festivaali': 'festivaalit',
    'festari': 'festarit',
    'juhla': 'juhlat',
    'alppi': 'alpit',
    'viikko': 'viikot',
    'amerikka': 'amerikat',
    'vihreä': 'vihreät',
    'filippiini': 'filippiinit',
    'yhdistynyt': 'yhdistyneet',
    'inen': 'iset',
    'kunta': 'kunnat', 
    }

pl_regex = '.*(%s)' % '|'.join(pluralia)


# Naively generate partitive form from lemma
par_suffixes = {
    (True, True): '[ia]',
    (True, False): '[iä]',
    (False, True): '[a]',
    (False, False): '[ä]',
}

par_forms = {
    'vuosi': 'vuotta',
    'aste': 'astetta',
    'kcal': 'kcal',
    }


def get_partitive(wform, lemma, morph):

    if re.search('[A-Z0-9/:.]', wform):
        return re.sub(':.+', '', wform)
    
    elif '[CASE=PAR]' in morph:
        return wform
    
    for nom, par in par_forms.items():
        if lemma.endswith(nom):
            return (lemma+'#').replace(nom+'#', par)
    
    if len(lemma) < 4:
        return lemma
    
    cons = lemma[-1] not in 'aeiouyäö'
    back = re.findall('[aou]', lemma[-5:]) != []
    
    return lemma + par_suffixes[(cons, back)]


def congr(morph1, morph2):

    """
    Check morphological analyses for agreement in NUM and CASE.
    """

    tags1 = re.findall('\[(CASE|NUM)=[A-Z]+]', morph1)
    tags2 = re.findall('\[(CASE|NUM)=[A-Z]+]', morph2)
    return tags1 == tags2


def get_lemma(wform, lemma, morph, tag=''):

    """
    Return lemma form (or nominative plural form) for nouns and nounlike words,
    otherwise return word form as is.
    """

    if re.match('POS=NOUN|POS=NUMERAL|POS=ADJECTIVE|SUBCAT=QUANTOR', morph):
        if '[NUM=PL]' in morph and not re.fullmatch(pl_regex, lemma) and re.match('Enamex(Loc|Evt|Org)', tag):
            for sg, pl in pl_forms.items():
                if lemma.endswith(sg):
                    return (lemma+'#').replace(sg+'#', pl)
            return lemma + '[t]'
        return lemma
    return wform.lower()


def parse_numex(entity, tag=numex_pfx):

    """
    Parse numerical expression (Numex).
    """

    normalized = []
    unit = entity.pop()

    while entity:
        
        wform, lemma, morph = entity.pop()

        if entity and 'NUMERAL' in morph:
            normalized.append(get_partitive(wform, lemma, morph))
        
        elif entity and re.search('PROPER.*CASE=GEN', morph) and tag == 'NumexMsrCur':
            normalized.append(wform.lower())

        else:
            normalized.append(lemma)

    normalized.reverse()
    wform, lemma, morph = unit

    if normalized[0] in ['yksi', '1']:
        normalized.append(lemma)
    else:
        normalized.append(get_partitive(wform, lemma, morph))
        
    return ' '.join(normalized)


def parse_timex(entity, tag=timex_pfx):

    """
    Parse expression of time such as dates are parsed differently (Timex).
    """

    normalized = []

    while entity:

        wform, lemma, morph = entity.pop()
        wform = wform.lower()

        if wform in ['aikana', 'välillä', 'aikaa']:
            normalized += [wform] + [e[0] for e in entity][::-1]
            normalized = normalized[::-1]
            return ' '.join(normalized)

        if wform.endswith('kuuta') and entity:

            wform2, lemma2, morph2 = entity.pop()

            if 'SUBCAT=ORD' in morph2:
                normalized.append(wform)
            else:
                normalized.append(lemma)
                
            wform, lemma, morph = wform2, lemma2, morph2

        if 'SUBCAT=ORD' in morph:
            normalized.append(lemma)
            if entity:
                wform, lemma, morph = entity.pop()
                if wform.endswith('kuun'):
                    normalized.append(wform)
                else:
                    normalized.append(lemma)

        elif re.fullmatch('[0-9]+[.]?', wform):
            normalized.append(wform)
        
        elif wform in ['vuonna', 'vuosina']:
            normalized.append(wform)
        
        elif re.fullmatch('vuosi|.+kuu|päivä', lemma):
            normalized.append(lemma)
        
        else:
            normalized.append(wform)
    
    normalized = normalized[::-1]
    return ' '.join(normalized)


def parse_enamex(entity, tag=enamex_pfx):

    """
    Parse proper name or similar expression (Enamex).
    """
    
    normalized = []
    wform, lemma, morph = entity.pop()
    
    if re.fullmatch('(18|19|20)[0-9][0-9]', wform) and tag.startswith('EnamexEvt') and entity:
        normalized.append(wform.lower())
        wform, lemma, morph = entity.pop()
    
    normalized.append(get_lemma(wform, lemma, morph, tag))
    
    while entity and not wform.startswith('-'):

        wform2, lemma2, morph2 = entity.pop()

        if re.search('POS=ADJECTIVE|SUBCAT=ORD|SUBCAT=QUANTOR', morph) and congr(morph, morph2):
            normalized.append(get_lemma(wform2, lemma2, morph2, tag))
        else:
            normalized.append(wform2.lower())
            break
        
        wform, lemma, morph = wform2, lemma2, morph2
    
    normalized = [wform.lower() for wform, lemma, morph in entity] + normalized[::-1]
    return ' '.join(normalized)


def is_endtag(nertag, tag=''):
    return any([
        nertag.startswith('</' + tag),
        nertag.startswith('<' + tag) and nertag.endswith('/>')
    ])


def main():

    tag_columns = [list() for i in range(max_depth)]
    analyses = []

    for n, line in enumerate(stdin, 1):

        line = line.lstrip(' \t').rstrip(' \n')

        if line:

            if '\t[POS=' not in line:
                stderr.write('WARNING: Line %i: Irregular morphological labels detected!\n' % n)

            fields = line.split('\t')

            try:
                wform, lemma, morph, semtag = fields[0:4]
            except:
                stderr.write('WARNING: Line %i: unexpected number of fields!\n' % n)
                exit(1)

            analyses.append((wform, lemma, morph, semtag, n))

            nertags = fields[4:] + [''] * max_depth
            nertags = nertags[0:max_depth]

            for nertag, tag_column in zip(nertags, tag_columns):
                tag_column.append(nertag)

        else:

            tag_columns = tag_columns[0:max_depth]
            entities = []

            for tag_column in tag_columns:

                tag = '#'
                tuples = []

                for analysis, nertag in zip(analyses, tag_column):

                    wform, lemma, morph, semtag, i2 = analysis

                    if nertag.startswith('<' + args.tag) and not nertag.startswith('</'):
                        i1 = i2
                        tag = nertag.strip('<>/')
                        tuples.append((wform, lemma.lower(), morph,))
                    elif tuples:
                        tuples.append((wform, lemma.lower(), morph,))

                    if is_endtag(nertag, tag):

                        if tag.startswith(enamex_pfx):
                            ent_str = parse_enamex(tuples, tag)

                        elif tag.startswith(timex_pfx):
                            ent_str = parse_timex(tuples, tag)

                        elif tag.startswith(numex_pfx):
                            ent_str = parse_numex(tuples, tag)

                        else:
                            ent_str = ' '.join([t[0] for t in tuples])

                        entities.append((i1, i2, ent_str, tag,))
                        tag = '#'
                        tuples = []

            entities.sort()

            for i1, i2, ent_str, tag in entities:
                print('%i,%i\t%s\t%s' % (i1, i2, ent_str, tag))

            tag_columns = [list() for i in range(max_depth)]
            analyses = []


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Extract entities found by FiNER, \
    normalize/lemmatize them and list in order of appearance.')
    parser.add_argument('--tag', type=str, default='', description='find entities whose tag begins with TAG')
    args = parser.parse_args()
    main()
