import shutil
import os
import datetime

os.chdir('counties')
counties = os.listdir('.')

starttime = datetime.datetime.now()
print(f"Time started: {starttime.strftime('%H:%M:%S')}\n")

for county in counties:
    if os.path.isdir(county):
        zipstart = datetime.datetime.now()
        print(f'{county} archive in process ...')
        shutil.make_archive(county, 'zip', county)
        print(f'{county}.zip created')
        print(f'Time spent for zipping: {datetime.datetime.now() - zipstart}\n')

print(f'Time consumed for all the archives: {datetime.datetime.now() - starttime}')