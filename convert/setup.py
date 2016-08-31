import argparse
import glob
import os
import configparser
import csv

'''
Sets up the program with the source file and draws in the data necessary to process the XML files into the Emdros format
'''


class Setup:

    mql_settings = {
    # fills with main.cfg
    }

    def __init__(self):
        # program greeting
        print('*'*20)
        print('This is SBLGNT2Emdros 1.0.')
        print('*'*20)


        # determine the source to be converted
        script_dir = os.path.dirname(os.path.abspath(__file__))

        config_f = script_dir+'/main.cfg'
        object_f = script_dir+'/objects.csv'

        # configure the database with the cfg file
        configparse = configparser.ConfigParser()
        with open(config_f,'r') as f: configparse.read_file(f)
        self.mql_settings['name'] = (configparse['database']['name'])
        input_dir = configparse['directory']['input']
        output_dir = configparse['directory']['output']

        mql_template_dir = '/templates_mql'
        inputs = [os.path.basename(x) for x in glob.glob("{}/*".format(input_dir)) if os.path.isdir(x)]

        # add argparser so users can define the source to be converted
        argsparser = argparse.ArgumentParser(description='Conversion of XML to Emdros')
        argsparser.add_argument(
            'input',
            type=str,
            choices=inputs,
            metavar='Input',
            help='Input selection for conversion',
        )
        self.args = argsparser.parse_args()

        # configure the database with the csv attributes for object types and enumerations
        self.mql_settings['object_types'] = {}
        with open(object_f, 'r') as f:
            csvfile = csv.reader(f)
            for row in csvfile:
                self.mql_settings['object_types'][row[0]] = [att for att in row if att is not row[0]]

        self.mql_settings['enumerations'] = {}

        # create the directory for the processed files
        self.output_dir = output_dir+'/'+self.args.input
        os.makedirs(self.output_dir, mode=0o777, exist_ok=True)
        # give the output file a complete pathway
        self.output_file = self.output_dir+'/{}.mql'.format(self.mql_settings['name'])
        # give the source a complete pathway
        self.input_dir = input_dir + '/' + self.args.input
        # give the mql template directory a complete pathway
        self.mql_template_dir = script_dir+mql_template_dir

