import re, logging, asyncio
from typing import Iterable, List
from dataclasses import dataclass
import pexpect
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", 
    format=FORMAT, 
    datefmt="[%X]", 
    handlers=[RichHandler()]
)

log = logging.getLogger("rich")


@dataclass
class Command:
    command: str
    code: int
    msg: str
    debug: bool = False
    
    def __post_init__(self):
        if self.debug:
            logging.debug(f'Command: {self.command} - Code: {self.code} - Msg: {self.msg}')

class HandlerEvents:
    def handler_call(self, number):
        logging.info(f'Calling to {number}')

    def handler_trying(self):
        logging.info('Trying to call')

    def handler_bye(self):
        logging.info('Bye')
    



class PhoneTools(HandlerEvents):
    def __init__(self, cmddebug: bool = False):
        self.child = pexpect.spawn('twinkle -c')
        self.DEBUG: bool = debug
        self.running: bool = False
        self.is_calling: bool = False
        self._prev_output: str = ''
        self._task_run_ = asyncio.create_task(self.run())

    async def __send_command__(self, command, expect) -> Command:
        self.child.sendline(command)
        code = 0
        msg: str = ''
        return Command(
            command=command, 
            code=code, 
            msg=msg, 
            debug=self.DEBUG)

    # COMMANDS 
    ###########
    async def call(self, number: str):
        call = await self.__send_command__(f'call {number.strip()}', 'received 100 trying')
        if call.code == 0:
            self.is_calling = True
        return call
    
    async def bye(self):
        bye = await self.__send_command__('bye', 'call ended')
        if bye.code == 0:
            self.is_calling = False
        return bye
    
    async def user(self):
        user = await self.__send_command__('user', '')
        return user
    
    async def send_help(self):
        self.child.sendline('help')
        help = await self.child.expect('help', async_=True)
        return {'code': help, 'msg': self.child.after.decode('utf-8')}

    async def quit(self):
        await self.__send_command__('quit', '')

    def close(self):
        self.child.close()
        self._task_run_.cancel()

    async def run(self):
        running = await self.child.expect('Twinkle', async_=True)
        self.running = True if running == 0 else False
        if self.DEBUG:
            logging.debug(f'Running: {self.running}')
        while self.running:
            try:
                # Read output
                out = self.child.readline().decode("utf-8").strip()
                if out != self._prev_output:
                    # Logging
                    if self.DEBUG:
                        logging.debug(f'READING: {out}')
                    if re.search(r'call', out):
                        self.handler_call(out.split('')[1])
                    elif re.search(r'Bye', out):
                        self.handler_bye()
                # set previous output
                self._prev_output = out
            except pexpect.exceptions.EOF:
                # exited
                self.running = False
            except pexpect.exceptions.TIMEOUT:
                # nothing happened for a while
                pass
            except KeyboardInterrupt:
                self.running = False
                await self.quit()
            except Exception as e:
                logging.error(e)
            await asyncio.sleep(0.1)  # Introduce a small delay to avoid tight looping

async def main():
    p = PhoneTools(debug=True)
    await p.call('010326')
    await asyncio.sleep(3)
    input('Close')
    await p.bye()
    await asyncio.sleep(3)
    await p.quit()
    p.close()

asyncio.run(main())
