import os
import json
import time
import datetime
import sys
import csv
import logging


logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_filename = os.path.join('c:\\','temp', 'scandir', 'scandir.log')
logging.basicConfig(format='%(asctime)s - %(levelname)s:%(message)s',
    filename=log_filename, sfilemode='a', level=logging.INFO)

def get_computer_name():
    return os.environ['COMPUTERNAME']

def get_total_size(entry_dic):
    return sum([entry["size"] for entry in entry_dic.values()])

def get_tree_size(path):
    """Return total size of files in path and subdirs. If
    is_dir() or stat() fails, print an error message to stderr
    and assume zero size (for example, file has been deleted).
    """
    total = 0
    # TODO: Shoud grab just 257 first characteres due to windows 
    # path size restrictions
    ext_path = path 
    try:
        scan = os.scandir(ext_path)
    except OSError as ex:
        logger.warning(f'Ignoring folder {ext_path} as you dont have read permissions.')
        # print(f'Ignoring folder {ext_path} as you dont have read permissions.')
        return 0
    for entry in scan:
        try:
            is_dir = entry.is_dir(follow_symlinks=False)
        except OSError as error:
            logger.error('Error calling is_dir():', error, file=sys.stderr)
            print('Error calling is_dir():', error, file=sys.stderr)
            continue
        if is_dir:
            try:
                total += get_tree_size(entry.path)
            except FileNotFoundError as ex:
                logger.warning(f'File {entry.path} not found.Probably file name too big.')
                print(f'File {entry.path} not found.Probably file name too big.')
        else:
            try:
                total += entry.stat(follow_symlinks=False).st_size
            except OSError as error:
                logger.error('Error calling stat():', error, file=sys.stderr)
                print('Error calling stat():', error, file=sys.stderr)
    return total

def get_file_size(path):
    return os.path.getsize(path)

def get_path_size(path):
    entry_dic = dict()
    total_size = 0
    for entry in os.scandir(path):
        print(entry)
        is_dir = entry.is_dir(follow_symlinks=False)
        try:
            if is_dir: 
                size = get_tree_size(entry)
            else:
                size = get_file_size(entry)
            total_size += size
        except PermissionError as ex:
            logger.info(f'Access is denied for path {entry}')
            print(f'Access is denied for path {entry}')
            size = 0
        entry_dic[entry] = {"size":  size, "is_dir": is_dir}

    return entry_dic

def output_to_screen(entry_dic):    
    total_size = 0
    folders_tuple = [('/' if value['is_dir'] else '', key, 
        value['size']) for key, value in entry_dic.items()]
    folders_tuple.sort(key=lambda s:s[2], reverse=True)
    for folder in folders_tuple:
        print(f' {folder[0]+str(folder[1])[11:-2]}'.ljust(30,'.'), 
            f'{round(folder[2]/1000000000,2)} GB')
        total_size += folder[2]
    print(f'Total size is {round(total_size/1000000000,2)} GB \n\n')

def create_json(initial_path, entry_dic):
    """
    Create a json file named scandir.json on 
    the same path as the executable.
    Json structure ex.:
    {"host_name": "023fs01", "initial_path": "e:/Dept", "total_size_gb": 194.33, 
    "scan_data": 
        [
            {"path": "/Users", "is_dir": "True", "size": 60.43},
            {"path": "/Windows", "is_dir": "True", "size": 34.98}
        ]
    }

    Args:
        initial_path: the initial path for the search to start from

        entry_dic: the dictionary with folders and their data (size and is_dir)
    """
    total_size = 0
    computer_name = get_computer_name()
    total_size = get_total_size(entry_dic)
    # fix the name of the folder and add server name and total size
    json_output = {key.name: value for key, value in entry_dic.items()}
    json_output = {"host_name": computer_name, 
        "initial_path": initial_path, "total_size": total_size, 
        "scan_data": json_output }

    with open('scandir.json', 'w') as json_file:
        json.dump(json_output, json_file)

def create_csv(initial_path, entry_dic):
    """
    Output the directory data onto a csv file on 
    the same path as the executable.
    csv structure ex.:
    host_name   path     Folder    is_dir  size(GB)
    023fs01     e:/Dept  /IT       True    60.4320
    ...
    ...
                         /         True    934.234 

    Args:
        initial_path - Search will be done for subdirectories of this path

        entry_dic - All hosts and folders that should be scanned
    """

    # convert to csv
    # everytime a csv is created, must have a diferent name: scandir_path_2020-01-01 10:00:00.234.csv
    csv_file_name = initial_path[3:].replace('/','-')
    csv_file = f'c:\\temp\\scandir\\scandir_{csv_file_name}_{datetime.datetime.now().strftime("%y-%m-%d-%H-%M")}.csv'
    host_name = get_computer_name()
    csv_columns = ["host_name", "path", "item_name", "is_dir", "size(GB)"]
    # create a list of items
    csv_list = []
    csv_final = []
    # change dic to a list and normalize things
    for key, value in entry_dic.items():
        csv_list.append([host_name, initial_path, 
            key.name, value['is_dir'], round(value['size']/1000000000,3)])
    
    csv_list = sorted(csv_list, key=lambda x: x[4], reverse=True)
    # inserts column names
    csv_list.insert(0, csv_columns) 
    
    for csv_item in csv_list:
        csv_final.append([csv_item[0], csv_item[1], csv_item[2], 
            csv_item[3], csv_item[4]])
            
    try:
        with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            writer.writerows(csv_final)
    except Exception as ex: # IOError
        logger.error(f"I/O error {ex}")

def main():
    start = time.time()
    result = ''
    try:
        folder = sys.argv[1]
        data = get_path_size(folder)
        #output_to_screen(data)
    except IndexError as ex:
        print('Missing start path. Ex: scandir c:/')
        sys.exit(0)
    end = time.time()
    logger.info(f'The search took {round(end-start)} secs!')
    # saving the file
    logger.info('Creating csv...')
    create_csv(folder, data)
    #logger.info('Creating json...')
    #create_json(folder, data)
    #input('hit any key...')

if __name__ == '__main__':
    main()
