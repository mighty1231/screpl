#ifndef WORKER_H
#define WORKER_H

#include <QObject>
#include <QThread>
#include <Windows.h>
#include <TlHelp32.h>
#include <QByteArray>
#include <QElapsedTimer>

#include "sharedregion.h"

// status flags
#define STATUS_NOPROCESS_FOUND 0
#define STATUS_PROCESS_FOUND 1
#define STATUS_REPL_FOUND 2

class Worker : public QThread
{
    Q_OBJECT

private:
    void run() override;

    static QString makeString(const char *from);
    static QString ignoreColor(const char *from);

    bool findProcess();
    bool findREPL();
    void communicateREPL();

    void process();

    // relative read or write
    inline bool writeRegionInt(int offset, int value);
    inline bool readRegionInt(int offset, int *value);


    QElapsedTimer last_interaction_timer;
    int last_framecount;

    // members
    QByteArray SIGNATURE;
    int status;

    int pageSize;
    PROCESSENTRY32 entry;
    HANDLE snapshot;

    HANDLE hProcess;

    int REPLRegion;
    SharedRegion *regiontmp;
    SharedRegion *region;

public:
    explicit Worker(QObject *parent = nullptr);
    void makeError(QString string);

signals:
    void signalError(QString string);

    // outputlog, loggerlog, display
    void update(QString applog, QString loggerlog, QString display);
    void metProcess(bool met);
    void metREPL(bool met);

};

#endif // WORKER_H
