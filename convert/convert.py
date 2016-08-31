import collections

'''

Steps:

1. Nest all non-object nodes as features of their object descendant nodes; delete non-object node.

2. Find all word nodes and place them in a dict paired with an assigned monad number. Use monad numbers to store monad sets.

3. Reassign all XML tree nodes to a monad set; add to a dict with the node's attributes.
    ...this is done by looking at all of the nodes' descendants and testing whether they are a word type node
    ......if so, the monad number is looked up with the monad dict.
    ...this process is performed for both the beginning and ending words in the nodes' descendants
    ...this creates the monad set, stored as a string with braces, '{ 1-10 }', in the dict with the attributes.
    ...at this stage in the process, we now have emdros-like objects!

4. Fill all the data slots in each object. Ex: every word object must have a slot for 'tense' for the mql database

5. As objects are created, a distinction is made between distributional and functional objects.
    ex: <phrase>  <noun_phrase1></noun_phrase1> <noun_phrase2></noun_phrase2>  </phrase>
    ...the phrase node is logged as a 'phrase'
    ...the two noun phrases are each logged as a 'phrase_atom'

6. Book, chapter, and verse objects are made by tracking and testing the nodeId (which contains the reference data).

6. Write objects to the database with the mql class, identifying them by the attribute 'Cat:' which ID's the appropriate object type.

'''

class Convert:

    object_conversion = {
        'word' : ['adj','adv','conj','det','inj','noun','num','prep','ptcl','pron','verb'],
        'phrase' : ['adjp','advp','np','nump','pp','vp'],
        'clause' : ['CL'],
        'sentence': ['SN'],
        'chapter' : ['chapter'],
        'book': ['book'],
        'verse': ['verse'],
        'no_obj' : ['ADV','IO','O','O2','S','P','V','VC']
    }

    object_template = {}

    sbl_book_codes = {
        '40': 'Matthew',
        '41': 'Mark',
        '42': 'Luke',
        '43': 'John',
        '44': 'Acts',
        '45': 'Romans',
        '46': 'ICorinthians',
        '47': 'IICorinthians',
        '48': 'Galatians',
        '49': 'Ephesians',
        '50': 'Philippians',
        '51': 'Colossians',
        '52': 'IThessalonians',
        '53': 'IIThessalonians',
        '54': 'ITimothy',
        '55': 'IITimothy',
        '56': 'Titus',
        '57': 'Philemon',
        '58': 'Hebrews',
        '59': 'James',
        '60': 'IPeter',
        '61': 'IIPeter',
        '62': 'IJohn',
        '63': 'IIJohn',
        '64': 'IIIJohn',
        '65': 'Jude',
        '66': 'Revelation'
    }

    trailers = ['.', ',', '; ', '·']

    no_enumeration = ['chapter', 'verse', 'sentenceId', 'nodeId', 'Start', 'End', 'Head', 'morphId', 'UnicodeLemma', 'Unicode',
                      'UnicodeTrailer', 'distributional_parent', 'functional_parent', 'Rule']

    def __init__(self, setup, sblgnt, mql):

        nodes = sblgnt.nodes
        node_descendants = sblgnt.node_descendants
        sentences = sblgnt.sentences
        monads = collections.OrderedDict()

        for otype in setup.mql_settings['object_types']:
            self.object_template[otype] = {x for x in setup.mql_settings['object_types'][otype]}

        # this method looks up the object type of a node
        def object_type(node):
            if nodes[node]['Cat'] == 'intj':
                if 'Unicode' in nodes[node]:
                    return 'word'
                else:
                    return 'clause'
            else:
                for type in self.object_conversion:
                    if nodes[node]['Cat'] in self.object_conversion[type]:
                        return type

        # A slight adjustment to the database is necessary to create the sentence objects.
        # The first node in the database is marked 'S' (usually 'subject') and contains only 3 attributes.
        # The sentence 'ID' has been harvested separately in SBLGNT since the sentence tag is different than node tags
        # 'S' is given a new tag 'SN' (sentence) and the sentence ID is added to the node.
        for n in nodes:
            if len(nodes[n]) == 3 and nodes[n]['Cat'] == 'S':
                nodes[n]['Cat'] = 'SN'
                nodes[n]['sentenceId'] = sentences[n]

        # remove all non-object nodes and list their attributes under the object nodes they modify (phrases, words)
        #   first, add the non-object attribute data to the objects they modify...
        for n in nodes:
            if nodes[n]['Cat'] in self.object_conversion['no_obj']:
                target=node_descendants[n]
                for t in target:
                    nodes[t]['function'] = nodes[n]['Cat']
        #   second, remove non-object nodes...
        nodes = collections.OrderedDict( (node, features) for (node, features) in nodes.items() if nodes[node]['Cat'] not in self.object_conversion['no_obj'])
        node_descendants = collections.OrderedDict( (node, nd) for (node, nd) in node_descendants.items() if node in nodes)

        # also remove non-object node descendants from each node's list of descendants
        new_node_descendants = collections.OrderedDict()
        for n in nodes:
            new_node_descendants[n] = [nd for nd in node_descendants[n] if nd in nodes]
        node_descendants = new_node_descendants

        # Create monad numbers for words. Then use monad numbers to assemble monad sets for objects comprised of the words.
        monad_counter = 0
        # Because the nodes dict is ordered, the code can simply iterate through all word nodes in the dict.
        for n in nodes:
            if object_type(n) == 'word':
                monad_counter += 1
                monads[n] = [monad_counter]
        # Here the code assembles monad sets for linguistic objects by using node_descendants.
        for n in nodes:
            if object_type(n) != 'word':
                beginning = None
                end = None
                for nd in node_descendants[n]:
                    if object_type(nd) == 'word':
                        beginning = monads[nd][0]
                        break           # breaks  loop at first word node descendant, leaving the first as 'beginning'
                for nd in node_descendants[n]:
                    if object_type(nd) == 'word':
                        end = monads[nd][0]    # iterates through all node descendants, leaving the last one as 'end'
                monads[n] = [beginning, end]

        # in the mql database, all objects which are the same carry the same attributes, whether they are fulfilled or not.
        # ex: both nouns and verbs are word objects, therefore a noun still carries a 'tense' attribute and a verb a 'gender'
        # unfulfilled attributes are simply left blank
        # the code below checks each node against the object template and fills in any missing attribute slots.
        for n in nodes:
            for data_slot in self.object_template[object_type(n)]:
                if data_slot not in nodes[n]:
                    nodes[n][data_slot] = ''

        # The SBLGNT database does not contain reference nodes. The code creates them here.
        # i.e. book, chapter, and verse
        nodes_sections = collections.OrderedDict()
        # Now, a method to remove zero padding from chapter and verse codes as they are found in SBLGNT
        def remove_padding(code):
            Letter1 = code[0] if code[0] != '0' else None
            Letter2 = code[1] if code[1] != '0' else None
            Letter3 = code[2]
            if Letter1:
                return Letter1+Letter2+Letter3
            elif Letter2:
                return Letter2+Letter3
            else:
                return Letter3

        # ...create the section nodes
        # ...in SBLGNT, section data is stored in the nodeId attribute of each node through a zero padded number
        # ...three if statements check the nodeId to see if the relevant section node has already been created or not
        # ...thus a 'book' node, for example, is created and stored as soon as the nodeId reflects a different book
        node_count = 0

        prev_book = None
        book_start = None
        book_end = None

        prev_chapter = None
        chapter_start = None
        chapter_end = None

        prev_verse = None
        verse_start = None
        verse_end = None

        # TODO: The code that creates the monad data here can be shortened significantly.
        for n in nodes:
            node_count += 1
            total_nodes = len(nodes)

            book_code = n[0]+n[1]    # first two numbers in nodeid refer to the book
            book_node = 'b'+book_code  # create a unique identifier as a temporary placeholder for the nodeid

            if book_node not in nodes_sections:
                nodes_sections[book_node] = {'book': self.sbl_book_codes[book_code],'Cat':'book'}

                if book_start:
                    book_end = monads[n][0] - 1
                    monads[prev_book] = [book_start, book_end]
                    prev_book = book_node
                    book_start = monads[n][0]

                else:
                    book_start = monads[n][0]
                    prev_book = book_node

            if node_count == total_nodes:
                book_end = monads[n][0]
                monads[book_node] = [book_start, book_end]

            chapter_code = remove_padding(n[2]+n[3]+n[4])
            chapter_node = 'c'+chapter_code+book_node
            if chapter_node not in nodes_sections:
                nodes_sections[chapter_node] = {'chapter': chapter_code, 'Cat': 'chapter'}

                if chapter_start:
                    chapter_end = monads[n][0] - 1
                    monads[prev_chapter] = [chapter_start, chapter_end]
                    prev_chapter = chapter_node
                    chapter_start = monads[n][0]

                else:
                    chapter_start = monads[n][0]
                    prev_chapter = chapter_node

            if node_count == total_nodes:
                chapter_end = monads[n][0]
                monads[chapter_node] = [chapter_start, chapter_end]


            verse_code = remove_padding(n[5]+n[6]+n[7])
            verse_node = 'v'+verse_code+chapter_node
            if verse_node not in nodes_sections:
                nodes_sections[verse_node] = {'verse': verse_code, 'Cat': 'verse', 'book':nodes_sections[book_node]['book'], 'chapter':nodes_sections[chapter_node]['chapter']}
                if verse_start:
                    verse_end = monads[n][0] - 1
                    monads[prev_verse] = [verse_start, verse_end]
                    prev_verse = verse_node
                    verse_start = monads[n][0]

                else:
                    verse_start = monads[n][0]
                    prev_verse = verse_node

            if node_count == total_nodes:
                verse_end = monads[n][0]
                monads[verse_node] = [verse_start, verse_end]

            nodes_sections[n] = nodes[n]
        nodes = nodes_sections

        # fill unicode trailer attribute and remove from unicode attribute
        for n in nodes:
            if object_type(n) == 'word':
                for letter in nodes[n]['Unicode']:
                    if letter in self.trailers:
                        nodes[n]['UnicodeTrailer'] = letter
                        nodes[n]['Unicode'] = nodes[n]['Unicode'].replace(letter, '')

        # replace node id numbers with consecutive object id numbers
        node_oid = collections.OrderedDict()
        monads_oid = collections.OrderedDict()
        oid_count = 0
        for n in nodes:
            oid_count += 1
            node_oid[oid_count] = nodes[n]
            node_oid[oid_count]['oType'] = object_type(n)
            monads_oid[oid_count] = monads[n]

        # TODO: preclude this step and use splits instead above where needed to simplify
        for m in monads_oid:
            if len(monads_oid[m]) == 2:
                monads_oid[m] = '{ '+ str(monads_oid[m][0])+'-'+str(monads_oid[m][1])+' }'
            else:
                monads_oid[m] = '{ ' + str(monads_oid[m][0]) + ' }'

        self.nodes = node_oid
        self.object_type = object_type
        self.mql = mql
        self.setup = setup
        self.monads = monads_oid

        # create enumerations for the mql dump
        # this creates attribute types for objects
        # the first big loop populates the enumerations dict with all possible attributes for the particular type
        # the second big loop counts the total attributes for each enumeration and assigns each one a number (enumeration)


        # a slight adjustment is necessary for nodes carrying the 'HasDet' attribute for the purpose of assembling the enumerations
        # TODO: Here would be a place to insert any other default attributes for the purpose of enumerations
        for n in nodes:
            if 'HasDet' in nodes[n] and not nodes[n]['HasDet']:
                nodes[n]['HasDet'] = 'False'

        for n in self.nodes:
            if 'Person' in self.nodes[n]:
                if self.nodes[n]['Person'] == 'First':
                    del self.nodes[n]['Person']
                    self.nodes[n]['Person'] = 'frst'

        self.enumerations = {}

        for n in self.nodes:
            for attrib in self.nodes[n]:
                if attrib not in self.enumerations and attrib not in self.no_enumeration and self.nodes[n][attrib]:
                    self.enumerations[attrib]= {self.nodes[n][attrib].replace('-',''):None}
                elif attrib in self.enumerations and attrib not in self.no_enumeration  and self.nodes[n][attrib]:
                    self.enumerations[attrib].update({self.nodes[n][attrib].replace('-',''):None})

        # add the numbers and defaults for enumerations
        for enum in self.enumerations:
            attrib_count = len(self.enumerations[enum])+1
            self.enumerations[enum].update({'DEFAULT NA':0})
            for attrib in self.enumerations[enum]:
                if attrib != 'DEFAULT NA':
                    attrib_count -= 1
                    self.enumerations[enum].update({attrib: attrib_count})

        # TODO:  **TEMPORARY** Move the following code elsewhere and simplify:
        # A necessary adjustment because of the mql rejection of '-' in the rule_t attribute type
        for n in self.nodes:
            if 'Rule' in self.nodes[n]:
                self.nodes[n]['Rule'] = self.nodes[n]['Rule'].replace('-','')

        print(str(len(self.nodes))+' objects found...')

    def write_mql(self):
        mql = self.mql
        settings = self.setup.mql_settings
        enumerations = self.enumerations

        mql.add_note('Create database and switch to using it.')
        mql.create_database(settings['name'])
        mql.add_note('Create enumerations', big=True)

        print('Setting up database enumerations...')

        for enum in self.enumerations:
            mql.add_note('Enumeration '+enum+'_t')
            mql.enumerate(enum+'_t', self.enumerations[enum])

        mql.add_note('Create object types', big=True)

        print('Setting up database object types...')

        for object in self.object_template:
            mql.add_note('Object type '+ object)
            mql.create_object_type(object, self.object_template[object])

        mql.add_note('Create object data', big=True)

        print('Creating word objects...')

        mql.add_note('Create object data for object type word', big=True)
        mql.add_note('drop indexes')
        mql.drop_index('word')
        mql.init_object('word')
        for n in self.nodes:
            if self.nodes[n]['oType'] == 'word':
                mql.add_object(n, self.nodes[n], monads=self.monads[n])
        mql.go()
        mql.add_note('create indexes')
        mql.create_index('word')

        print('Creating linguistic objects...')

        for object in self.object_template:
            if object != 'word':
                mql.add_note('Create object data for object type {}'.format(object), big=True)
                mql.add_note('drop indexes')
                mql.drop_index(object)
                mql.init_object(object)
                for n in self.nodes:
                    if self.nodes[n]['oType'] == object:
                        mql.add_object(n, self.nodes[n], monads= self.monads[n])
                mql.go()
                mql.add_note('create indexes')
                mql.create_index(object)

        mql.add_note('VACUUM database', big=True)
        mql.vacuum()