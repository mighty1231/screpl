#include "worker.h"
#include <string.h>
#include <QtGlobal>
#include <QMutexLocker>
#include <QtDebug>

#include "blocks/appoutput.h"
#include "blocks/appstack.h"
#include "blocks/blindmode.h"
#include "blocks/gametext.h"
#include "blocks/logger.h"
#include "blocks/profile.h"

static int BRIDGE_PROTOCOL_VER_1 = 0x20200604;
static int BRIDGE_PROTOCOL_VER_2 = 0x20200616;

static inline bool IsSTRSectionMBI(MEMORY_BASIC_INFORMATION *mbi) {
    return (mbi->State == MEM_COMMIT)
                    && (mbi->Type == MEM_PRIVATE)
                    && (mbi->Protect == PAGE_READWRITE);
}

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
    available_protocol(BRIDGE_PROTOCOL_VER_2), status(0), hProcess(NULL), REPLRegion(0)
{
    SYSTEM_INFO info;
    GetSystemInfo(&info);
    pageSize = info.dwPageSize;

    entry.dwSize = sizeof(PROCESSENTRY32);

    query_buffer = new QByteArray();
}

void Worker::setConnection(MainWindow *_window)
{
    QObject *window = reinterpret_cast<QObject *>(_window);
    // initialize blocks
    qRegisterMetaType<QVector<uint>>("QVector<uint>");

    connect(this, SIGNAL(metProcess(bool)),
            window, SLOT(metProcess(bool)),
            Qt::QueuedConnection);
    connect(this, SIGNAL(metREPL(bool, int)),
            window, SLOT(metREPL(bool, int)),
            Qt::QueuedConnection);
    connect(this, SIGNAL(signalError(QString)),
            window, SLOT(setError(QString)),
            Qt::QueuedConnection);
    connect(this, SIGNAL(sentCommand(QString)),
            window, SLOT(sentCommand(QString)),
            Qt::QueuedConnection);

    AppOutputBlock *aob = new AppOutputBlock();
    aob->moveToThread(this);
    connect(aob, SIGNAL(updateAppOutput(QString)),
            window, SLOT(updateAppOutput(QString)),
            Qt::QueuedConnection);
    blocks.push_back(aob);

    AppStackBlock *asb = new AppStackBlock();
    asb->moveToThread(this);
    connect(asb, SIGNAL(updateAppStack(QStringList)),
            window, SLOT(updateAppStack(QStringList)),
            Qt::QueuedConnection);
    blocks.push_back(asb);

    BlindModeDisplayBlock *bmdb = new BlindModeDisplayBlock();
    bmdb->moveToThread(this);
    connect(bmdb, SIGNAL(updateBlindModeDisplay(QString)),
            window, SLOT(updateBlindModeDisplay(QString)),
            Qt::QueuedConnection);
    blocks.push_back(bmdb);

    GameTextBlock *gtb = new GameTextBlock();
    gtb->moveToThread(this);
    connect(gtb, SIGNAL(updateGameText(QString)),
            window, SLOT(updateGameText(QString)),
            Qt::QueuedConnection);
    blocks.push_back(gtb);

    LoggerBlock *lb = new LoggerBlock();
    lb->moveToThread(this);
    connect(lb, SIGNAL(updateLoggerLog(QString)),
            window, SLOT(updateLoggerLog(QString)),
            Qt::QueuedConnection);
    blocks.push_back(lb);

    ProfileBlock *pb = new ProfileBlock();
    pb->moveToThread(this);
    connect(pb, SIGNAL(updateProfileNames(QStringList)),
            window, SLOT(updateProfileNames(QStringList)),
            Qt::QueuedConnection);
    connect(pb, SIGNAL(updateProfiles(QVector<uint>, QVector<uint>, QVector<uint>)),
            window, SLOT(updateProfiles(QVector<uint>, QVector<uint>, QVector<uint>)),
            Qt::QueuedConnection);
    blocks.push_back(pb);
}


Worker::~Worker() {
    for (auto b:blocks) {
        delete b;
    }
    delete query_buffer;
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
    uint written;
    bool found = false;
    while (startAddr  <= 0xFFFE0000) {
        if (!VirtualQueryEx(hProcess, (void *)startAddr, &mbi, sizeof(mbi))) {
            status = STATUS_NOPROCESS_FOUND;
            emit metProcess(false);
            makeError(QString("VirtualQueryEx"));
            CloseHandle(hProcess);
            return false;
        }
        if (IsSTRSectionMBI(&mbi)) {
            query_buffer->resize(mbi.RegionSize + SIGNATURE.length());
            written = readSTRSection(startAddr, query_buffer->data(), mbi.RegionSize + SIGNATURE.length());
            if (written == 0) {
                status = STATUS_NOPROCESS_FOUND;
                emit metProcess(false);
                makeError("ReadProcessMemory");
                CloseHandle(hProcess);
                return false;
            }

            query_buffer->resize(written);

            // search REPL-signature
            int idx = query_buffer->indexOf(SIGNATURE);
            if (idx != -1) {
                if (found) {
                    makeError("SC-REPL Signature duplicate");
                    return false;
                }
                REPLRegion = startAddr + idx;

                int _protocol;
                if (!readRegionInt(offsetof(SharedRegionHeader, bridge_protocol), &_protocol)) {
                    status = STATUS_NOPROCESS_FOUND;
                    emit metProcess(false);
                    makeError("Read protocol");
                    CloseHandle(hProcess);
                    return false;
                }
                if (_protocol != available_protocol) {
                    makeError(QString("Bridge protocol conflict (%1). expected %2")
                              .arg(_protocol).arg(available_protocol));
                    return false;
                }

                found = true;
            }
        }
        startAddr += mbi.RegionSize;
    }

    if (found) {
        status = STATUS_REPL_FOUND;
        last_inversed_system_millis = -1;
        emit metREPL(true, REPLRegion);
        return true;
    } else {
        emit signalError("REPL not found");
    }
    return false;
}

void Worker::communicateREPL()
{
    // Too much milk solution #3, busy-waiting by A
    if (!writeRegionInt(offsetof(SharedRegionHeader, note_to_sc), 1)) { // leave note A
        status = STATUS_PROCESS_FOUND;
        emit metREPL(false, REPLRegion);
        makeError("WriteProcessMemory, leave note A");
        return;
    }
    int noteB;
    for (int i=0; i<10; i++) {
        if (!readRegionInt(offsetof(SharedRegionHeader, note_from_sc), &noteB)) {
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
    QVector<RegionBlock *> block_computed;
    QString _command_tmp;
    uint regionSize;
    if (!readRegionInt(offsetof(SharedRegionHeader, region_size), (int *)&regionSize)) {
        status = STATUS_PROCESS_FOUND;
        emit metREPL(false, REPLRegion);
        makeError("ReadProcessMemory, read region size");
        return;
    }

    char *all_region = new char[regionSize];
    SIZE_T written = readSTRSection(REPLRegion, all_region, regionSize);
    if (written != regionSize) {
        status = STATUS_PROCESS_FOUND;
        emit metREPL(false, REPLRegion);
        makeError("ReadProcessMemory, read region");
        delete[] all_region;
        return;
    }

    // minimal operation between leaving note A
    SharedRegionHeader *header = (SharedRegionHeader *) all_region;

    // Check the section is not polluted (exits game...)
    if (memcmp(header->signature, SIGNATURE.constData(), SIGNATURE.size())
        || header->note_to_sc != 1
        || header->note_from_sc != 0
        || header->bridge_protocol != available_protocol
        || header->region_size != regionSize ) {
        status = STATUS_PROCESS_FOUND;
        emit metREPL(false, REPLRegion);
        makeError("ReadProcessMemory, read region pollution check");
        delete[] all_region;
        return;
    }

    // send command
    if (header->command[0] == 0) {
        QMutexLocker locker(&command_mutex);
        if (!command.isEmpty()) {
            strncpy_s(header->command, command.toLocal8Bit().constData(), 300);
            _command_tmp = command;
            command.clear();
        }
    }

    // restore note
    header->note_to_sc = 0;

    // blocks
    int *blockptr = (int *)(((char *)all_region) + sizeof(SharedRegionHeader));
    uint offset = sizeof(SharedRegionHeader);
    bool processed;
    while (offset < regionSize) {
        int signature = *blockptr++;
        uint block_size = *blockptr++;
        Q_ASSERT(offset + block_size <= regionSize);

        processed = false;
        for (auto b:blocks) {
            if (b->getSignature() == signature){
                b->immediateProcess(blockptr, block_size);
                processed = true;
                block_computed.push_back(b);
                break;
            }
        }
        if (!processed) {
            /* memory has changed */
            status = STATUS_PROCESS_FOUND;
            emit metREPL(false, REPLRegion);
            makeError("process, recognizing blocks");
            delete[] all_region;
            return;
        }
        Q_ASSERT(processed);

        offset += 8 + block_size;
        blockptr += block_size / 4;
    }

    written = writeSTRSection(REPLRegion, all_region, regionSize);
    if (written != regionSize) {
        status = STATUS_PROCESS_FOUND;
        emit metREPL(false, REPLRegion);
        makeError("WriteProcessMemory, write region");
        delete[] all_region;
        return;
    }

    // some heavy evaluations
    if (!_command_tmp.isNull())
        emit sentCommand(_command_tmp);

    // check heartbeat
    if (last_inversed_system_millis == header->inversed_system_millis) {
        // nothing to do
        if (last_interaction_timer.elapsed() > 2000) {
            // called when user returns to lobby.
            // (Note. REPL signature is not disappeared automatically on game exit)
            status = STATUS_PROCESS_FOUND;
            writeRegionInt(0, 0); // invalidate signature
            emit metREPL(false, REPLRegion);
            makeError("REPL interaction timeout");
            delete[] all_region;
            return;
        }
        delete[] all_region;
        return;
    } else {
        last_inversed_system_millis = header->inversed_system_millis;
        last_interaction_timer.start();
    }

    delete[] all_region;

    for (auto b:block_computed) {
        b->afterProcess();
    }
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

SIZE_T Worker::readSTRSection(uint address, void *buf, SIZE_T length)
{
    /*
     * read memory (address ~ address+length-1) and write to buf.
     * returns length of written bytes
     * */

    char *dest = (char *)buf;

    SIZE_T totalRemainingLength = length;
    uint currentAddress = address;
    SIZE_T total_written = 0;

    MEMORY_BASIC_INFORMATION mbi;
    while (totalRemainingLength > 0)
    {
        if (!VirtualQueryEx(hProcess, (void *)currentAddress, &mbi, sizeof(mbi))
                || !IsSTRSectionMBI(&mbi)) {
            return total_written;
        }

        uint memoryEndAddress = (uint) mbi.BaseAddress + mbi.RegionSize;
        SIZE_T bytesToRead = qMin((SIZE_T)memoryEndAddress - currentAddress, totalRemainingLength);
        SIZE_T written;

        if (!ReadProcessMemory(hProcess, (void *)currentAddress, dest + total_written, bytesToRead, &written)
                || written != bytesToRead) {
            return total_written;
        }
        total_written += bytesToRead;
        currentAddress += bytesToRead;
        totalRemainingLength -= bytesToRead;
    }

    return total_written;
}

SIZE_T Worker::writeSTRSection(uint address, const void *buf, SIZE_T length)
{
    /*
     * read memory (address ~ address+length-1) and write to buf.
     * returns length of written bytes
     * */

    char *src = (char *)buf;

    SIZE_T totalRemainingLength = length;
    uint currentAddress = address;
    SIZE_T total_written = 0;

    MEMORY_BASIC_INFORMATION mbi;
    while (totalRemainingLength > 0)
    {
        if (!VirtualQueryEx(hProcess, (void *)currentAddress, &mbi, sizeof(mbi))
                || !IsSTRSectionMBI(&mbi)) {
            return total_written;
        }

        uint memoryEndAddress = (uint) mbi.BaseAddress + mbi.RegionSize;
        SIZE_T bytesToRead = qMin((SIZE_T)memoryEndAddress - currentAddress, totalRemainingLength);
        SIZE_T written;

        if (!WriteProcessMemory(hProcess, (void *)currentAddress, src + total_written, bytesToRead, &written)
                || written != bytesToRead) {
            return total_written;
        }
        total_written += bytesToRead;
        currentAddress += bytesToRead;
        totalRemainingLength -= bytesToRead;
    }

    return total_written;
}
