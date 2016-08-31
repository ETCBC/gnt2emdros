from setup import Setup
from SBLGNT import SBLGNT
from mql import Mql
from convert import Convert

setup = Setup()
print('Extracting node data from XML files...')
sblgnt = SBLGNT(setup)
mql = Mql(setup, setup.output_file)
print('Beginning conversion into MQL objects...')
convert = Convert(setup, sblgnt, mql)
print('Writing objects to MQL file...')
convert.write_mql()
print('Conversion successful! '+str(len(convert.nodes))+' objects created in database \"'+setup.mql_settings['name']+'\"')