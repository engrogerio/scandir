import wmi
import os
import filecmp
import shutil
import logging
import json

# TODO: Implement decent log messages 

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logger = logging.getLogger(__name__)
log_filename = os.path.join(BASE_DIR,'scandir', 'logs', 'scandir.log')
os.makedirs(os.path.dirname(log_filename), exist_ok=True)
logging.basicConfig(format='%(asctime)s - %(levelname)s:%(message)s', 
    filename=log_filename, filemode='a', level=logging.INFO)


def mkdir(host_name, file_dest):
    try:
        cmd = f'pushd {os.path.dirname(file_dest)} & mkdir scandir & popd'
        os.system(cmd)
        print(f'Trying to run {cmd} on server {host_name}...')    
    except Exception as ex:
        print(f'Server {host_name} access attempt caused unexpected exception: {ex}')

def undeploy_script(host_name, path):
    # TODO: Implement this
    """

    Check if the folder scandir exists on the server and 
    remove the folder.

    """
    logger.info('Checking Jython library version on server %s.' % host_name)
    file_dest = os.path.join( '\\\\', host_name, path, 'scandir.py')
    try:
        file_exists_on_server = os.path.isfile(file_dest)
        if file_exists_on_server:
            try:
                logger.info(f'Removing script on host {host_name}')
                os. remove(file_dest)
                return True
            except Exception as ex:
                logger.error('Deployment of the script failed returning the error: %s.' % ex)
        else:
            logger.info('No script on server %s.' % host_name)
    except FileNotFoundError:
        logger.error('Script undeploy fails due to the path %s was not found.' % file_dest)
    except PermissionError:
        logger.error('User does not have permission on folder %s.' % file_dest)

def deploy_script(host_name, folder_path):
    """

    Check if the file scandir.py does not exists on the server or 
    if it is not equal to the source.
    In any case, overwrite the destin file with the source file.

    Args:
        folder_path: path of the folder to deploy the script

    Raise:
       FileNotFoundError
       PermissionError

    """
    logger.info('Checking script version on server %s.' % host_name)
    file_source = os.path.join(BASE_DIR,'scandir', 'dist', 'scandir.exe')
    file_dest = os.path.join('\\\\',host_name,'c$', 'temp', 'scandir', 'scandir.exe')
    file_exists_on_host = os.path.isfile(file_dest)
    file_is_newest_version = False
    if file_exists_on_host:
        file_is_newest_version = filecmp.cmp(file_source, file_dest)

    if not file_is_newest_version or not file_exists_on_host:
        try:
            logger.info('Deploying scandir to the host %s.' % host_name)
            # create the folder c:/temp/scandir on the host if does not exists
            remote_dir = os.path.dirname(file_dest)
            logger.info(f'Creating folder {os.path.dirname(folder_path)}...')
            mkdir(host_name, remote_dir)
            shutil.copyfile(file_source, file_dest)
        except Exception as ex:
            logger.error('Deployment of the script failed returning the error: %s.' % ex)

           
    else:
        logger.info('No script update needed on server %s.' % host_name)

def get_response_from_code(code):
    responses = {
        0: "Successful completion",
        2: "Access denied",
        3: "Insufficient privilege",
        8: "Unknown failure",
        9: "Path not found",
        21:"Invalid parameter",
        22: "Other",
        4294967295: "Other"
    }    
    return responses.get(code, f"WMI returned '{code}'")

def show_processes(wmi_server):
    for process in wmi_server.Win32_Process(): 
        print(f"{process.ProcessId:<10} {process.Name}")

def run_remote(host_name:str, remote_script_path:str, scan_path:str):
    """
    Run script on the server
    host_name: Server host name or ip
    remote_script_path: Complete path including script file name: ex. c:/temp/scandir/scandir.exe 
    scan_path: The inicial folder to get the size of the sub folders. ex. e:/Dept
    """
    result = process_id = result = None
    try:
        c = wmi.WMI(host_name) #, user=user, password=password)
        cmd = f'{os.path.join(remote_script_path)} {scan_path}'
        logger.info(f'Trying to run {cmd} on server {host_name}...')    
        process_id, result = c.Win32_Process.Create(CommandLine=cmd)
    except Exception as ex:
        logger.error(f'Server {host_name} access attempt caused unexpected exception: {ex}')

    if result == 0:
        logger.info(f'Process {process_id} started successfully!')
    else:    
        logger.info(get_response_from_code(result))
    # show_processes(c)  

def get_hosts_from_file(file: str)->dict:
    with open(file,'r') as hosts:
        host_name_dict = json.loads(hosts.read())
    return host_name_dict

def main():
    remote_script_path = "c:\\temp\\scandir\\scandir.exe"
    hosts_file = os.path.join(BASE_DIR,'scandir','hosts.json')
    host_name_dict = get_hosts_from_file(hosts_file)       
    for host_name, path_to_scan in host_name_dict.items():
        deploy_script(host_name, remote_script_path)
        run_remote(host_name, remote_script_path, path_to_scan)

if __name__ == '__main__':
    main()