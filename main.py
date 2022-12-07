import json
import paramiko
import os
import sys
import socket
from conf import ssh_conf as conf_file
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Ssh:
    "Class to connect to remote server"

    def __init__(self):
        self.ssh_output = None
        self.ssh_error = None
        self.ssh_error_text = None
        self.client = None
        self.host= conf_file.HOST
        self.username = conf_file.USERNAME
        self.password = conf_file.PASSWORD
        self.timeout = float(conf_file.TIMEOUT)
        self.commands = conf_file.COMMANDS
        self.pkey = conf_file.PKEY
        self.port = conf_file.PORT

    def connect(self):
        "Login to the remote server"
        try:
            #Paramiko.SSHClient can be used to make connections to the remote server and transfer files
            print("Establishing ssh connection...")
            self.client = paramiko.SSHClient()
            #Parsing an instance of the AutoAddPolicy to set_missing_host_key_policy() changes it to allow any host.
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            #Connect to the server
            if (self.password == ''):
                private_key = paramiko.RSAKey.from_private_key_file(self.pkey)
                self.client.connect(hostname=self.host, port=self.port, username=self.username,pkey=private_key ,timeout=self.timeout, allow_agent=False, look_for_keys=False)
                print("Connected to the server",self.host)
            else:
                self.client.connect(hostname=self.host, port=self.port,username=self.username,password=self.password,timeout=self.timeout, allow_agent=False, look_for_keys=False)
                print("Connected to the server",self.host)
        except paramiko.AuthenticationException:
            print("Authentication failed, please verify your credentials")
            result_flag = False
        except paramiko.SSHException as sshException:
            print("Could not establish SSH connection: %s" % sshException)
            result_flag = False
        except socket.timeout as e:
            print("Connection timed out")
            result_flag = False
        except Exception as e:
            print('\nException in connecting to the server')
            print('PYTHON SAYS:',e)
            result_flag = False
            self.ssh_error = e.strerror
            self.client.close()
        else:
            result_flag = True

        return result_flag

    def execute_command(self,commands):
        self.ssh_output = None
        result_flag = True
        try:
            if self.connect():
                for command in commands:
                    print("Executing command --> {}".format(command))
                    stdin, stdout, stderr = self.client.exec_command(command)

                    text_stderr = stderr.read()
                    text_stdout = stdout.read()

                    self.ssh_output = text_stdout
                    self.ssh_error = text_stderr

                    if self.ssh_error:
                        print("Problem occurred while running command:" + command + " The error is " + str(text_stderr))
                        #print("Problem occurred while running command:" + command + " The error is " + self.ssh_error)
                        result_flag = False
                    else:
                        print("Command execution completed successfully", command, str(text_stdout))
                    #data = stdout.read() + stderr.read()
                    #print(data)
                    #self.ssh_error_text = data
                    self.client.close()
            else:
                print("Could not establish SSH connection")
                result_flag = False
        except socket.timeout as e:
            self.write(str(e),'debug')
            self.client.close()
            result_flag = False
        except paramiko.SSHException:
            print("Failed to execute the command!",command)
            self.client.close()
            result_flag = False

        return result_flag

def parseJsonData(datafile):
    with open(datafile, 'r', encoding='utf-8') as jsonFile: # открыть файл
        jsonData = json.load(jsonFile) #загнали все из файла в переменную
        print(jsonData)
        print("Checking if nested JSON key exists or not")
        if 'hosts' in jsonData:
            print("Printing nested JSON key-value", jsonData['hosts'])
            for cluster in jsonData['hosts']:
                print("cluster --> ", cluster)
                if cluster in jsonData['hosts']:

                    ssh_obj = Ssh()
                    ssh_obj.host = jsonData['hosts'][cluster]['host']
                    if ssh_obj.execute_command(ssh_obj.commands) is True:
                        print("Commands executed successfully\n")
                        result_comand(ssh_obj, jsonData, cluster)
                        #jsonData['hosts'][cluster]['result'] = ssh_obj.ssh_output
                    else:
                        jsonData['hosts'][cluster]['result'] = "Unable to execute the commands"
                        jsonData['hosts'][cluster]['error'] = ssh_obj.ssh_error
                        print("Unable to execute the commands")

                    print("host --> ", jsonData['hosts'][cluster]['host'])

    with open(datafile, "w") as jsonFile:
        json.dump(jsonData, jsonFile)
        print("Result Json --> ", jsonData)

def result_comand(res, jsonData, cluster):
    lines = str(res.ssh_output)
    for line in lines.split("\n"):
        # Ignore the last line of the last report.
        if line.startswith("b""") and len(line) < 5:
            jsonData['hosts'][cluster]['result'] = '-'
            break
        parts = line.split()
        if parts:
            resultstr = parts[0]
            #if not account in EXPECTED:
            #    print(f"Entry '{line}' is a surprise on {server}.")
            #result = {'result': resultstr}
            #jsonData['hosts'][cluster].append(result)
            jsonData['hosts'][cluster]['result'] = resultstr
            print(jsonData)

if __name__=='__main__':
    parseJsonData('host.json')


