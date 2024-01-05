import re, logging, time
from typing import Iterable, List, Any
from dataclasses import dataclass
from multiprocessing import Process, Event, Manager
import pexpect
from rich.logging import RichHandler
import threading
import signal


# Rich Logging
FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", 
    format=FORMAT, 
    datefmt="[%X]", 
    handlers=[RichHandler()]
)

log = logging.getLogger("rich")


# Dataclasses
@dataclass
class Command:
    command: str
    code: int
    msg: str
    debug: bool = False
    
    def __post_init__(self):
        if self.debug:
            logging.debug(f'Command: {self.command} - Code: {self.code} - Msg: {self.msg}')

@dataclass
class Call:
    number: str
    id: int
    states : List[str]


# Events
class HandlerEvents:
    def handler_call(self, number):
        logging.info(f'Calling to {number}')

    def handler_trying(self):
        logging.info('Trying to call')

    def handler_bye(self):
        logging.info('Bye')



# PhoneTools
class PhoneTools(HandlerEvents):
    """
    Twinkle CLI wrapper async.

    Twinkle version: 1.10.3 - Feb 19, 2022
    
    https://github.com/LubosD/twinkle.git
    
    This script was based on the project https://github.com/forkcs/twinkle-py.git 
    """
    def __init__(self, cmd: List[str] = ['twinkle', '-c'], debug: bool = False):
        """
        :param cmd: a command to execute. defaults to ['twinkle', '-c']
        :param debug: print Twinkle input to console
        """

        self.DEBUG: bool = debug
        self.cmd = cmd
        self._running: bool = False
        self._prev_output: str = ''
        self._on_call: bool = False
        self._on_mute: bool = False
        self.child = pexpect.spawn('twinkle -c')
        
    ##############
    # Properties #
    ##############
    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, value):
        self._running = value

    @property
    def prev_output(self):
        return self._prev_output

    @prev_output.setter
    def prev_output(self, value):
        self._prev_output = value

    @property
    def on_call(self):
        return self._on_call

    @on_call.setter
    def on_call(self, value):
        self._on_call = value

    @property
    def on_mute(self):
        return self._on_mute

    @on_mute.setter
    def on_mute(self, value):
        self._on_mute = value

    ############
    # Commands #
    ############
    def __send_command__(self, command) -> Any:
        """
        Send command
        """
        if self.DEBUG:
            log.debug(f'__send_command__: {command}')
        self.child.sendline(command)

    def __read_stream__(self) -> Iterable[str]:
        while self.running:
            try:
                # Read output
                line = self.child.readline().decode("utf-8").strip()
                # Logging
                if self.DEBUG:
                    log.debug(f'READING: {line}')
                if line == self._prev_output \
                    or line == '':
                        continue
                self.prev_output = line
                yield line
                # set previous output
            except pexpect.exceptions.EOF:
                self.__stop_reding__()
                self.quit()
            except pexpect.exceptions.TIMEOUT:
                line = 'TIMEOUT'
                log.error(f'{line}')
                continue
            except Exception as e:
                log.error(e)
                continue
    
    def __stop_reding__(self):
        if self.DEBUG:
            log.debug(f'__stop_reding__:')
        self.running = False
    
    # COMMANDS 
    ###########
    def call(self, number: str):
        self.__send_command__(f'call {number.strip()}')
        self.on_call = True

    def answer(self):
        self.__send_command__('answer')
        self.on_call = True
    
    def bye(self):
        self.__send_command__('bye')
        self.on_call = False

    def mute(self):
        self.__send_command__('mute')
    
    def un_mute(self):
        self.__send_command__('mute')
    
    def dtmf(self, digits: str):
        self.__send_command__(f'dtmf {digits.strip()}')
    
    def redial(self):
        self.__send_command__('redial')

    def register(self):
        self.__send_command__('register')
    
    def deregister(self):
        self.__send_command__('deregister')
    
    def fetch_registered(self):
        self.__send_command__('fetch_reg')
    
    def set_line(self, line: str):
        self.__send_command__(f'line {line.strip()}')
    
    def dnd(self):
        self.__send_command__('dnd')
    
    def hold(self):
        self.__send_command__('hold')
    
    def un_hold(self):
        self.__send_command__('retrieve')

    def user(self, name: str = None) -> None:
        if name is None:
            name = ''
        self.__send_command__(f'user {name}')

    def presence(self, state: str) -> None:
        self.__send_command__(f'presence {state}')

    def auto_answer(self) -> None:
        self.__send_command__('auto_answer')

    def quit(self):
        self.__send_command__('quit')
        self.__stop_reding__()

    def run(self) -> None:
        self.running = True
        if self.DEBUG:
            logging.debug(f'Running: {self.running}')
        # Read stream
        for line in self.__read_stream__():
            log.info(line)
            if 'call' in line:
                number = line.split('call')[1].strip()
                log.info(f'Calling to {number}')
                self.handler_call(number)
            elif 'bye' in line:
                self.handler_bye()
            elif 'registering phone' in line:
                sip = line.split(' ')
                log.info(f'Registering phone {sip}')
            time.sleep(0.1)

def main():
    p = PhoneTools(debug=True)
    try:
        def signal_handler(sig, frame):
            print("Pressione Ctrl+C novamente para sair.")
            signal.signal(signal.SIGINT, signal.SIG_DFL)

        signal.signal(signal.SIGINT, signal_handler)
        # Criar uma thread para executar o método run
        thread = threading.Thread(target=p.run)

        # Iniciar a thread
        thread.start()

        for _ in range(5):
            start = input('Iniciar?: ')
            if start.lower() == 'n':
                break
            p.call('010326')
            time.sleep(5)
            input('Fechar')
            p.bye()

    finally:
        try:
            # Aguardar a thread terminar antes de chamar p.quit()
            thread.join()
        except KeyboardInterrupt:
            pass  # Ignorar a exceção quando Ctrl+C é pressionado novamente

        p.quit()

main()
