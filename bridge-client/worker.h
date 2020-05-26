#ifndef WORKER_H
#define WORKER_H

#include <QObject>
#include <QThread>
#include <Windows.h>
#include <TlHelp32.h>
#include <QByteArray>
#include <QElapsedTimer>
#include <QMutex>

#include "sharedregionheader.h"
#include "regionblock.h"

// status flags
#define STATUS_NOPROCESS_FOUND 0
#define STATUS_PROCESS_FOUND 1
#define STATUS_REPL_FOUND 2

QT_FORWARD_DECLARE_CLASS(MainWindow);

class Worker : public QThread
{
    Q_OBJECT

private:
    void run() override;

    bool searchProcess();
    bool searchREPL();
    void communicateREPL();

    void process();

    QMutex command_mutex;
    QString command;

    // relative read or write
    SIZE_T readSTRSection(uint address, void *buf, SIZE_T length);
    SIZE_T writeSTRSection(uint address, const void *buf, SIZE_T length);
    inline bool writeRegionInt(int offset, int value);
    inline bool readRegionInt(int offset, int *value);

    QElapsedTimer last_interaction_timer;
    int last_inversed_system_millis;

    // members
    QByteArray SIGNATURE;
    int status;

    int pageSize;
    PROCESSENTRY32 entry;
    HANDLE snapshot;
    HANDLE hProcess;

    QByteArray *query_buffer;

    int REPLRegion;

    QVector<RegionBlock *> blocks;

public:
    explicit Worker(QObject *parent = nullptr);
    ~Worker();

    static QString makeString(const char *from);
    static QString ignoreColor(const char *from);

    void setConnection(MainWindow *);
    void makeError(QString string);
    bool setCommand(QString new_cmd);

signals:
    void signalError(QString string);
    void metProcess(bool met);
    void metREPL(bool met, int sharedregion_ptr);

    void sentCommand(QString cmd);
};

#endif // WORKER_H
