import psutil, os
import settings

class InputError(Exception):
    pass

    
def get_processes():
    processes = []
    with open(os.sep.join([settings.CWD, '.process']).replace('//', '/'), 'r') as fin:
        for i in fin.readlines():
            index = i.index(':')
            processes.append(Process(int(i[:index]), i[index + 1:].replace('\n', '')))
    return processes

class Process:
    def __init__(self, proc, name=None):
        if isinstance(proc, int) or (isinstance(proc, str) and all([i in '0123456789' for i in proc])):
            self.pid = int(proc)
            if name != None:
                self.proc_name = name
            else:
                self.proc_name = psutil.Process(pid=proc).name()

        else:
            raise InputError('Not valid input!')

    def __str__(self):
        return "{}:{}".format(self.pid, self.proc_name)

    def isAlive(self):
        return psutil.pid_exists(self.pid) and (psutil.Process(self.pid).name() == self.proc_name)

    def write(self):
        current = set()
        if os.path.isfile(os.sep.join([settings.CWD, '.process']).replace('//', '/')):
            with open(os.sep.join([settings.CWD, '.process']).replace('//', '/'), 'r') as fin:
                for i in fin.readlines():
                    current.add(i.replace('\n', ''))
        
        current.add(str(self))
        with open(os.sep.join([settings.CWD, '.process']).replace('//', '/'), 'w') as fin:
            for i in current:
                fin.write(i + '\n')
