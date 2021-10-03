import os
import re
import pandas as pd

empty_origins = []
no_docs_inn = []
only_one_screen = []
empty_school = []
regex = re.compile('\d{10}')

for root, dirs, files in os.walk('counties'):
    if regex.search(os.path.basename(root)) and dirs == [] and files == []:
        empty_school.append(regex.search(root)[0])
    if not regex.search(root) and dirs == []:
        empty_origins.append(os.path.basename(root))
    if 'documents' in root and files == []:
        no_docs_inn.append(regex.search(root)[0])
    if regex.search(root) and len(files) == 1:
        only_one_screen.append(regex.search(root)[0])

# print('Empty schools: ', len(empty_school))
# print('Empty origins: ', len(empty_origins))
# print('No docs: ', len(no_docs_inn))
# print('Only one screen: ', len(only_one_screen))

df = pd.read_excel('urls.xlsx', 
                    skiprows=3,
                    usecols=[1, 2, 3, 4])
df.columns = ['origin', 'inn', 'name', 'url']
df['inn'] = df['inn'].astype('str')

df.loc[df['inn'].isin(empty_school), 'empty_school'] = 1
df.loc[df['inn'].isin(only_one_screen), 'only_one_screen'] = 1
df.loc[df['inn'].isin(no_docs_inn), 'no_docs'] = 1
df.loc[df['origin'].isin(empty_origins), 'empty_origin'] = 1
# print(empty_school)
print('Empty schools: ', len(df.loc[df['empty_school'] == 1]))
print('Only one screen: ', len(df.loc[df['only_one_screen'] == 1]))
print('No docs: ', len(df.loc[df['no_docs'] == 1]))
print('Empty origin: ', len(df.loc[df['empty_origin'] == 1]))

df.to_excel('spaces.xlsx', index=False)