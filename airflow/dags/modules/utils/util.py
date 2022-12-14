import json


def get_config_param(config_entry):
    with open('/opt/airflow/dags/modules/config.json') as f:
        conf = json.load(f)
        return conf[config_entry]


def timestamp_to_time(ts):
    return ts[0:4]+'-'+ts[4:6]+'-'+ts[6:8]+' '+ts[8:10]+':'+ts[10:12]+':'+ts[12:]


def move_file_to_archive(file):
    dir = file.split('/')
    dir.insert(-1, 'archive')
    new_dir = '/'.join(dir)

    import os
    os.rename(file, new_dir)


def filter_files_by_extension(files, extension):
    if (extension[0] == '.'):
        ext = extension
    else:
        ext = f'.{extension}'

    return filter(lambda file: file[-len(ext):] == ext, files)


if __name__ == '__main__':
    print(get_config_param('energa_password'))
