import os
import json

import pandas as pd

from modules.utils import util


class FileProcessor():

    def __init__(self):
        self._org_files_directory = f'{util.get_config_param("file_dir")}/energa/org_files'
        self._transformed_files_directory = f'{util.get_config_param("file_dir")}/energa'

    def _get_scrape_time_from_filename(self, filename):
        return filename[filename.rfind('_')+1:-4]

    def _get_energy_type_from_filename(self, filename):
        if "Raport_A-" in filename:
            return 'produced'
        if "Raport_A+" in filename:
            return 'used'

        return 'not specified'

    def transform_to_json(self):

        files = os.listdir(self._org_files_directory)
        files = util.filter_files_by_extension(files=files, extension='xls')

        for f in files:

            df = pd.read_excel(f'{self._org_files_directory}/{f}')

            df.drop(columns=['Suma'], inplace=True)
            df.rename(columns={'Data': 'collectTime'}, inplace=True)
            df.set_index('collectTime', inplace=True)

            df_json = df.to_json(orient='table')
            scrape_time = self._get_scrape_time_from_filename(f)
            energy_type = self._get_energy_type_from_filename(f)

            df_json_2 = json.loads(df_json)
            df_json_2.pop('schema')

            final_json = {'source': 'energa', 'scrape_time': scrape_time,
                          'energy_type': energy_type, 'data': df_json_2['data']}
            json_object = json.dumps(final_json)

            print(json_object)

            with open(f'{self._transformed_files_directory}/{f[:-4]}.json', 'w') as f:
                f.write(json_object)
