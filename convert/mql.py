
'''
Constructs the mql files from the SBLGNT nodes using plain text mql templates.
'''

class Mql:


    data_format = {
        'enumerate' : '{attrib} = {number}{punc}',
        'obj_attrib_string': '{attrib} : {type} DEFAULT \"\"{punc}',  # for object type creation
        'obj_attrib_integer': '{attrib} : {type} DEFAULT 0{punc}',
        'obj_attrib_type': '{attrib} : {type} DEFAULT NA{punc}',
        'create_obj_string': '{attrib}:=\"{string}\"{punc}',          # for creating object data
        'create_obj_integer': '{attrib}:={integer}{punc}',
        'create_obj_type': '{attrib}:={string}{punc}',
        'add_obj_string': '{attrib}:=\"{type}\"{punc}',
        'add_obj_integer':'{attrib}:={type}{punc}',
        'add_obj_type': '{attrib}:={type}{punc}'
    }

    data_format_key = {
        'book': ['string', 'string'],
        'Cat': ['type', 'Cat_t'],
        'chapter': ['integer', 'integer'],
        'verse': ['integer', 'integer'],
        'nodeId': ['string', 'string'],
        'Start': ['integer', 'integer'],
        'End': ['integer', 'integer'],
        'Head': ['string', 'string'],
        'Rule': ['string', 'string'],
        'function': ['type', 'function_t'],
        'HasDet': ['type', 'HasDet_t'],
        'morphId': ['string', 'string'],
        'UnicodeLemma': ['string', 'string'],
        'Unicode': ['string', 'string'],
        'UnicodeTrailer': ['string', 'string'],
        'Gender': ['type', 'Gender_t'],
        'Case': ['type', 'Case_t'],
        'Number': ['type', 'Number_t'],
        'Mood': ['type', 'Mood_t'],
        'Tense': ['type', 'Tense_t'],
        'Voice': ['type', 'Voice_t'],
        'typ': ['type', 'typ_t'],
        'Person': ['string', 'string'],
        'ClType': ['type', 'ClType_t'],
        'sentenceId': ['string', 'string'],
        'Degree':['type','Degree_t']
    }

    # string, integer, type

    def __init__(self, setup, file):
        self.file = open(file,'w')    # an output file to write the mql code to
        self.mql_settings = setup.mql_settings
        self.mql_template_dir = setup.mql_template_dir

    # This function converts a dict of data into a string with the appropriate formatting for writing to the mql file
    # Because of the various formats needed to be written, the function relies on a set of switches to define the format
    # These switches are stored in the dict, data_type


    # TODO: Simplify the bottom two methods into one
    def format_enumeration(self, dic):
        transform = ''
        count = len(dic)
        for k in dic:
            count -= 1
            transform += self.data_format['enumerate'].format(attrib=k, number=dic[k], punc=',\n' if count > 0 else '')
        return transform

    def format_create_obj(self, dic):
        count = len(dic)
        transform = ''
        for k in dic:
            count -= 1
            transform += self.data_format['obj_attrib_'+self.data_format_key[k][0]].format(attrib=k, type=self.data_format_key[k][1],punc= ';\n' if count > 0 else ';')
        return transform

    def format_add_obj(self, dic):
        count = len(dic)
        transform = ''
        for k in dic:
            count -= 1
            # TODO: Simplify?
            if self.data_format_key[k][0] == 'type':
                transform += self.data_format['add_obj_'+self.data_format_key[k][0]].format(attrib=k, type=dic[k] if dic[k] else 'NA',punc= ';\n' if count > 0 else ';')
            else:
                transform += self.data_format['add_obj_' + self.data_format_key[k][0]].format(attrib=k, type=dic[k] if dic[k] else '', punc=';\n' if count > 0 else ';')
        return transform


    def format_line(self, line, data={}):
        line = line.format(**data)  # ** returns all the keyword arguments in this dict
        line = line.replace('<', '{')
        line = line.replace('>', '}')
        return line

    def write_data(self, name, data, template, monads=None,):      # name and data are meant loosely; in the template file, '{name}' is used where most appropriate as well as '{data}'.
        template = self.mql_template_dir+template
        with open(template, 'r') as template:
            for line in template:
                self.file.write(self.format_line(line, data={'name': name, 'data': data, 'monads': monads}))

    def create_database(self, name):
        self.name = name
        self.write_data(self.name, '', '/mql_create.txt')

    def enumerate(self, name, data):
        self.name = name
        self.data = self.format_enumeration(data)
        self.write_data(self.name, self.data,'/mql_enumerate.txt')

    def create_object_type(self, name, data):
        self.name = name
        self.data = self.format_create_obj(data)
        self.write_data(self.name, self.data,'/mql_create_object.txt')

    def init_object(self, object_type):
        self.write_data(object_type, '', '/mql_obj_init.txt')

    def add_object(self, name, data, monads=None):  # 'initialize' stored as the object type; needs to be switched on at the beginning of the loop.
        self.name = name
        self.data = self.format_add_obj(data)
        self.monads = monads
        self.write_data(self.name, self.data,'/mql_add_object.txt', monads=self.monads)

    def drop_index(self, name):
        self.name = name
        self.write_data(self.name, '', '/mql_drop_index.txt')

    def create_index(self, name):
        self.name = name
        self.write_data(self.name, '', '/mql_create_index.txt')

    def add_note(self, statement, big=False):
        self.statement = statement
        self.big = big
        self.write_data('', self.statement, '/mql_add_note.txt') if self.big else self.file.write('// {}\n'.format(self.statement))

    def go(self):
        self.write_data(self.name, '', '/mql_go.txt')

    def vacuum(self):
        self.write_data('', '', '/mql_vacuum.txt')
