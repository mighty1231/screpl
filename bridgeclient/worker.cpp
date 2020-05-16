#include "worker.h"
#include <string.h>

#include <QtDebug>


Worker::Worker(QObject *parent) : QThread(parent),
    SIGNATURE("\xc1\xfa\x55\x60\x5f\xca\x38\x5e\x91\xe4\x38\x43\x08\x64\x6a\x1c"
              "\x60\x7f\xbe\x3e\xba\x92\x84\xb2\x3f\x2d\xef\xb6\x1c\xee\x29\xa4"
              "\x56\x47\x10\xfb\x7b\xd7\xb6\x4b\x5c\xf6\xae\x4f\xe4\xa5\xc1\xd1"
              "\x96\x19\x14\x4b\xb4\x7b\x53\x7e\x39\xe8\x30\x5a\x59\x1f\x07\x5d"
              "\x07\x03\x1a\xc4\xff\x09\xe4\xa3\xa5\x99\xd9\x81\x43\xea\x55\x21"
              "\xc3\xf5\x40\x86\x0d\x08\xee\xb8\x47\x0c\x3c\x90\xb0\x51\x44\xef"
              "\xe1\x2d\xcd\x94\x8c\x01\xec\x84\xae\x2b\x62\x03\xb3\x89\xc0\x28"
              "\x30\x6d\x0e\xd8\xf4\xe4\x06\x15\x25\xb1\x74\x0f\x44\x27\xa1\x6e"
              "\xfe\x1f\x23\xa4\xcd\x7b\xa7\x84\x67\xdb\xa5\x77\x9a\x81\xc0\x12"
              "\xeb\xc0\x54\xa2\x37\x1e\x9c\xc6\x64\x24\x64\xe2\x33\x3f\x71\xe2", 160),
    status(0), hProcess(NULL), REPLRegion(0)
{
    SYSTEM_INFO info;
    GetSystemInfo(&info);
    pageSize = info.dwPageSize;

    entry.dwSize = sizeof(PROCESSENTRY32);

    regiontmp = new SharedRegion();
    region = new SharedRegion();
    app_output_buffer = new char[APP_OUTPUT_MAXSIZE + 1];
}

Worker::~Worker() {
    delete[] app_output_buffer;
    delete region;
    delete regiontmp;
}

void Worker::run()
{
    forever {
        if (QThread::currentThread()->isInterruptionRequested()) {
            break;
        }
        switch(status) {
        case STATUS_NOPROCESS_FOUND:
            if (!searchProcess()) {
                sleep(1);
                break;
            }
        case STATUS_PROCESS_FOUND:
            if (!searchREPL()) {
                sleep(1);
                break;
            }
        case STATUS_REPL_FOUND:
            communicateREPL();
            msleep(50);
        }
    }
}

bool Worker::searchProcess()
{
    // find process
    snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, NULL);
    if (Process32First(snapshot, &entry) == TRUE) {
        while (Process32Next(snapshot, &entry) == TRUE) {
//            QString file = QString::fromWCharArray(entry.szExeFile);
//            qDebug() << file << wcscmp(entry.szExeFile, L"StarCraft.exe");
            if (wcscmp(entry.szExeFile, L"StarCraft.exe") == 0) {
                hProcess = OpenProcess(
                            PROCESS_VM_READ
                            | PROCESS_VM_WRITE
                            | PROCESS_VM_OPERATION
                            | PROCESS_QUERY_INFORMATION,
                            FALSE,
                            entry.th32ProcessID);
                if (hProcess) {
                    status = STATUS_PROCESS_FOUND;
                    emit metProcess(true);
                    CloseHandle(snapshot);
                    return true;
                } else {
                    makeError("OpenProcess");
                    CloseHandle(snapshot);
                    return false;
                }
            }
        }
    }
    CloseHandle(snapshot);
    return false;
}

bool Worker::searchREPL()
{
    // query memory
    MEMORY_BASIC_INFORMATION mbi;
    unsigned int startAddr = pageSize;
    QByteArray *buffer = NULL;
    SIZE_T written;
    bool found = false;
    while (startAddr  <= 0xFFFE0000) {
        if (!VirtualQueryEx(hProcess, (void *)startAddr, &mbi, sizeof(mbi))) {
            status = STATUS_NOPROCESS_FOUND;
            emit metProcess(false);
            makeError(QString("VirtualQueryEx"));
            CloseHandle(hProcess);
            return false;
        }
        if ((mbi.State & MEM_COMMIT)
                && (mbi.Protect & PAGE_READWRITE)
                && !(mbi.Protect & PAGE_GUARD)) {
            buffer = new QByteArray(mbi.RegionSize, 0);

            // get buffer
            if (!ReadProcessMemory(hProcess, (void *)startAddr, buffer->data(), mbi.RegionSize, &written)) {
                if (GetLastError() == 299) {
                    goto next;
                }

                status = STATUS_NOPROCESS_FOUND;
                emit metProcess(false);
                makeError("ReadProcessMemory");
                CloseHandle(hProcess);
                delete buffer;
                return false;
            }
            if (written != mbi.RegionSize) {
                status = STATUS_NOPROCESS_FOUND;
                emit metProcess(false);
                makeError("ReadProcessMemory, size");
                CloseHandle(hProcess);
                delete buffer;
                return false;
            }

            // search REPL-signature
            int idx = buffer->indexOf(SIGNATURE);
            if (idx != -1) {
                if (found) {
                    makeError("SC-REPL Signature duplicate");
                    delete buffer;
                    return false;
                }
                found = true;
                REPLRegion = startAddr + idx;
            }
        next:
            delete buffer;
        }
        startAddr += mbi.RegionSize;
    }

    if (found) {
        status = STATUS_REPL_FOUND;
        last_framecount = -1;
        emit metREPL(true, REPLRegion);
        return true;
    } else {
        emit signalError("REPL not found");
    }
    return false;
}

QString Worker::traverseHeaps()
{
    HEAPLIST32 hl;

    HANDLE hHeapSnap = CreateToolhelp32Snapshot(TH32CS_SNAPHEAPLIST, GetProcessId(hProcess));

    hl.dwSize = sizeof(HEAPLIST32);

    if ( hHeapSnap == INVALID_HANDLE_VALUE )
    {
        return QString::asprintf("CreateToolhelp32Snapshot failed (%d)\n", GetLastError());
    }

    QString string;
    if( Heap32ListFirst( hHeapSnap, &hl ) )
    {
        do
        {
            HEAPENTRY32 he;
            ZeroMemory(&he, sizeof(HEAPENTRY32));
            he.dwSize = sizeof(HEAPENTRY32);

            if( Heap32First( &he, GetProcessId(hProcess), hl.th32HeapID ) ) {
                string += QString::asprintf( "\nHeap ID: %d\n", hl.th32HeapID );
                do
                {
                    string += QString::asprintf( "Block size: %d\n", he.dwBlockSize );
                    he.dwSize = sizeof(HEAPENTRY32);
                } while( Heap32Next(&he) );
            }
            hl.dwSize = sizeof(HEAPLIST32);
        } while (Heap32ListNext( hHeapSnap, &hl ));
    }
    else
        string += QString::asprintf ("Cannot list first heap (%d)\n", GetLastError());

    CloseHandle(hHeapSnap);
    qDebug() << string;
    return string;
}

void Worker::communicateREPL()
{
    // Too much milk solution #3, busy-waiting by A
    if (!writeRegionInt(offsetof(SharedRegion, noteToSC), 1)) { // leave note A
        status = STATUS_PROCESS_FOUND;
        emit metREPL(false, REPLRegion);
        makeError("WriteProcessMemory, leave note A");
        return;
    }
    int noteB;
    for (int i=0; i<10; i++) {
        if (!readRegionInt(offsetof(SharedRegion, noteFromSC), &noteB)) {
            status = STATUS_PROCESS_FOUND;
            emit metREPL(false, REPLRegion);
            makeError("ReadProcessMemory, leave note B");
            return;
        }
        // while (note B) do nothing
        if (noteB == 0)
            break;
        msleep(50);
    }
    if (noteB == 1) {
        status = STATUS_PROCESS_FOUND;
        emit metREPL(false, REPLRegion);
        makeError("ReadRegionInt 10 times");
        return;
    }
    process();
    msleep(150);
}

void Worker::process()
{
    SIZE_T written;
    QString _command_tmp;
    if (!ReadProcessMemory(
                hProcess,
                (void *) REPLRegion,
                regiontmp,
                sizeof(SharedRegion),
                &written) || written != sizeof(SharedRegion)) {
        status = STATUS_PROCESS_FOUND;
        emit metREPL(false, REPLRegion);
        makeError("ReadProcessMemory, read region");
        return;
    }

    // minimal operation between leaving note A
    // send command
    if (regiontmp->command[0] == 0) {
        command_mutex.lock();
        if (!command.isEmpty()) {
            strncpy_s(regiontmp->command, command.toLocal8Bit().constData(), 300);
            _command_tmp = command;
            command.clear();
        }
        command_mutex.unlock();
    }
    memcpy(region, regiontmp, sizeof(SharedRegion));
    regiontmp->noteToSC = 0;
    regiontmp->app_output_sz = 0;

    // restore note
    if (!WriteProcessMemory(
                hProcess,
                (void *) REPLRegion,
                regiontmp,
                sizeof(SharedRegion),
                &written) || written != sizeof(SharedRegion)){
        status = STATUS_PROCESS_FOUND;
        emit metREPL(false, REPLRegion);
        makeError("WriteProcessMemory, write region");
        return;
    }

    // some heavy evaluations
    if (!_command_tmp.isNull())
        emit sentCommand(_command_tmp);

    // check framecount
    if (last_framecount == region->frameCount) {
        // nothing to do
        if (last_interaction_timer.elapsed() > 2000) {
            // called when user returns to lobby.
            // (Note. REPL signature is not disappeared automatically on game exit)
            status = STATUS_PROCESS_FOUND;
            writeRegionInt(0, 0); // invalidate signature
            emit metREPL(false, REPLRegion);
            makeError("REPL interaction timeout");
            return;
        }
        return;
    } else {
        last_framecount = region->frameCount;
        last_interaction_timer.start();
    }

    // app output
    memcpy(app_output_buffer, region->app_output, region->app_output_sz);
    region->app_output[region->app_output_sz] = 0;
    QString app_output = QString::fromUtf8(region->app_output);

    // log
    static int last_log_index = 0;
    QString logger_log;
    for (int i=last_log_index; i<region->log_index; i++) {
        int line = i % LOGGER_LINE_COUNT;
        logger_log.append(ignoreColor(region->logger_log[line]));
        logger_log.append('\n');
    }
    last_log_index = region->log_index;

    // display
    QString display;
    int idx = region->displayIndex;
    for (int i=0; i<11; i++) {
        QString line = ignoreColor(region->display[idx]);
        display.append(line);
        if (!line.endsWith('\n'))
            display.append('\n');
        idx += 1;
        if (idx == 11)
            idx = 0;
    }
    display.append("\n--------\n");
    display.append(ignoreColor(region->display[12]));
    display.append('\n');

    // blindmode display
    QString blindmode_display = ignoreColor(region->blindmode_display);

    emit update(app_output, logger_log, display, blindmode_display);
}

bool Worker::writeRegionInt(int offset, int value)
{
    SIZE_T written;
    int ret = WriteProcessMemory(
            hProcess,
            (void *) (REPLRegion + offset),
            &value,
            sizeof(int),
            &written);
    if (ret == 0 || written != 4) {
        return false;
    }
    return true;
}

bool Worker::readRegionInt(int offset, int *value)
{
    SIZE_T written;
    int ret = ReadProcessMemory(
            hProcess,
            (void *) (REPLRegion + offset),
            value,
            sizeof(int),
            &written);
    if (ret == 0 || written != 4) {
        return false;
    }
    return true;
}

void Worker::makeError(QString label)
{
    QString message;
    const DWORD error = GetLastError();
    if (error != ERROR_SUCCESS) // I just like to be explicit.
    {
      // Fetch the error message.
      LPTSTR errorMessage = NULL;
      const DWORD size = FormatMessage(
                  FORMAT_MESSAGE_FROM_SYSTEM |
                  FORMAT_MESSAGE_IGNORE_INSERTS |
                  FORMAT_MESSAGE_ARGUMENT_ARRAY |
                  FORMAT_MESSAGE_ALLOCATE_BUFFER,NULL,
                  error,0,(LPTSTR) &errorMessage,0, NULL );

      // Copy the error message to a QString object.
      if (size > 0) {
          #ifdef UNICODE
           message = QString::fromWCharArray(errorMessage, size);
          #else
           message = QString::fromLocal8Bit(errorMessage, size);
          #endif
      }

      // Free the error message buffer.
      if (errorMessage != NULL) {
        HeapFree(GetProcessHeap(), 0, errorMessage);
      }
    }

    // {label} - {GetLastError()}: {ErrorMessage}
    QString total = label + " - " + QString::number(error, 10) + ": " + message;
    emit signalError(total);
}

bool Worker::setCommand(QString new_cmd)
{
    bool ret;
    command_mutex.lock();
    if (command.isNull()) {
        command = new_cmd;
        ret = true;
    } else {
        ret = false;
    }
    command_mutex.unlock();
    return ret;
}

QString Worker::makeString(const char *ptr)
{
    QByteArray ba;
    unsigned char c = *ptr;
    while (c != 0) {
        // string escape
        if ((1 <= c && c <= 0x1F && c != '\n') || c==0x7F) {
            ba.append("\\x");
            ba.append(QString::number(c,  16));
        } else if (c == '\\') {
            ba.append("\\\\");
        } else {
            ba.append(c);
        }
        c = *(++ptr);
    }

    return QString::fromUtf8(ba);
}

QString Worker::ignoreColor(const char *ptr)
{
    QByteArray ba;
    unsigned char c = *ptr;
    while (c != 0) {
        // string escape
        if (!(1 <= c && c <= 0x1F && c != '\n') && c!=0x7F)
            ba.append(c);
        c = *(++ptr);
    }

    return QString::fromUtf8(ba);
}
