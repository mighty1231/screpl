"""Defines LoggerBlock"""
from eudplib import *

from screpl.apps.logger import (
    buf_start_epd,
    log_index,
    LOGGER_LINE_SIZE,
    LOGGER_LINE_COUNT,
)
from screpl.bridge_server import block

class LoggerBlock(block.BridgeBlock):
    """Provides logs from Logger

    .. code-block:: C

        struct LoggerBlock {
            int log_index;
            char logger_log[LOGGER_LINE_COUNT][LOGGER_LINE_SIZE];
        };
    """
    signature = b'LOGB'

    def get_buffer_size(self):
        return 4 + LOGGER_LINE_COUNT * LOGGER_LINE_SIZE

    def update_content(self):
        prev_log_index = EUDVariable(0)
        quot, rem = f_div(prev_log_index, LOGGER_LINE_COUNT)
        rel = rem * (LOGGER_LINE_SIZE // 4)
        if EUDInfLoop()():
            EUDBreakIf(prev_log_index == log_index)

            f_repmovsd_epd(
                EPD(self + 4) + rel,
                buf_start_epd + rel,
                LOGGER_LINE_SIZE // 4
            )

            DoActions([
                rel.AddNumber(LOGGER_LINE_SIZE // 4),
                rem.AddNumber(1),
                prev_log_index.AddNumber(1)
            ])
            Trigger(
                conditions=rem.Exactly(LOGGER_LINE_COUNT),
                actions=[
                    rem.SetNumber(0), rel.SetNumber(0)
                ]
            )
        EUDEndInfLoop()
        SeqCompute([(EPD(self), SetTo, log_index)])
