#include "logger.h"

LoggerBlock::LoggerBlock()
{

}

void LoggerBlock::immediateProcess(void *block, uint size)
{
    Q_ASSERT(size + sizeof(QObject) == sizeof(LoggerBlock));
    memcpy(&log_index, block, size);
}

void LoggerBlock::afterProcess()
{
    static int last_log_index = 0;
    QString string;
    for (int i=last_log_index; i<log_index; i++) {
        int line = i % LOGGER_LINE_COUNT;
        string.append(ignoreColor(logger_log[line]));
        string.append('\n');
    }
    last_log_index = log_index;

    emit updateLoggerLog(string);
}