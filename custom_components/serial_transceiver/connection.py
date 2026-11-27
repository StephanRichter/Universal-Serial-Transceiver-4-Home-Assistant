"""
Connection implementation of the Serial Transceiver

This class encapsulates communication with a tty device.

This code is derived from https://github.com/RyanMathewson/home-assistant-onkyo-serial
"""
from __future__ import annotations
from collections.abc import Callable
from homeassistant.exceptions import HomeAssistantError
from .const import CLOSE_TIMEOUT, DOMAIN, RECONNECT_DELAY, SEND_GAP, UTF8
import asyncio, logging, serial_asyncio_fast, time

_LOGGER = logging.getLogger(__name__)

class SerialConnection:
    # Owns the serial port

    def _handle_frame(self, frame: bytes) -> None:
        text = frame.decode(UTF8, errors="ignore").strip()
        _LOGGER.debug(f"Receiver received '{text}'")
        if self._serial:
            self._serial.handle_value(text)


    def __init__(self, port: str, baud_rate: int) -> None:
        self.port : str                      = port
        self.baud_rate : int                 = baud_rate
        self.connected                       = False
        self._queue: asyncio.Queue[str]      = asyncio.Queue()
        self._last_error: str | None         = None
        self._serial: SerialReceiver | None = None

    def link_receiver(self, receiver: SerialReceiver | None) -> Callable:
        """sets the _serial field of the connection. This is where incoming messages are sent to"""
        _LOGGER.debug("installed sensor" if receiver else "uninstalled sensor")
        self._serial = receiver
        return lambda: self.link_receiver(None)

    async def _read_loop(self, reader: asyncio.StreamReader) -> None:
        """asynchronous waiting for incoming messages"""
        while True:
            try:
                frame = await reader.readline()
            except asyncio.IncompleteReadError as err:
                raise ConnectionError("Serial port closed") from err
            if not self.connected:
                self.connected   = True
                self._last_error = None
            self._handle_frame(frame)

    async def run(self) -> None:
        """Hold the port open, reconnecting whenever it is lost."""
        while True:
            try:
                await self._session()
            except asyncio.CancelledError:
                raise
            except Exception as err:  # noqa: BLE001 - any failure means reconnect
                message = f"{type(err).__name__}: {err}"
                if message != self._last_error:
                    _LOGGER.warning("Connection to %s lost: %s", self.port, message)
                    self._last_error = message
            self.connected = False
            await asyncio.sleep(RECONNECT_DELAY)

    async def send(self, message: str) -> None:
        """Queue a message"""
        if not self.connected:
            raise HomeAssistantError(translation_domain=DOMAIN, translation_key="disconnect") from ConnectionError(f"Receiver not connected on {self.port}")
        await self._queue.put(message)

    async def _session(self) -> None:
        _LOGGER.debug(f"Trying to connect to {self.port} with {self.baud_rate} symbols/sec")
        reader, writer = await serial_asyncio_fast.open_serial_connection(url=self.port,baudrate=self.baud_rate,bytesize=8,parity="N",stopbits=1,xonxoff=False,rtscts=False,exclusive=True)
        if not self.connected:
            self.connected   = True
            self._last_error = None
            _LOGGER.info("Receiver connected on %s", self.port)

        self._queue = asyncio.Queue()
        tasks = [
            asyncio.create_task(self._read_loop(reader)),
            asyncio.create_task(self._write_loop(writer))
        ]
        try:
            done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                task.result()
        finally:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            writer.close()
            # Release the port's lock before a reload or retry tries to reopen it.
            try:
                await asyncio.wait_for(writer.wait_closed(), CLOSE_TIMEOUT)
            except (OSError, TimeoutError):
                pass

    async def _write_loop(self, writer: asyncio.StreamWriter) -> None:
        """asynchronous waiting for queued messages. These will be sent on the serial line"""
        while True:
            command = await self._queue.get()
            writer.write(f"{command}\n".encode(UTF8))
            await writer.drain()
            await asyncio.sleep(SEND_GAP)
