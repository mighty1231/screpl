#ifndef WORKER_H
#define WORKER_H

#include <QObject>
#include <QThread>
#include <Windows.h>
#include <TlHelp32.h>
#include <QByteArray>
#include <QElapsedTimer>
#include <QMutex>

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

    bool searchProcess();
    bool searchREPL();
    void communicateREPL();

    void process();
    QString traverseHeaps();

    QMutex command_mutex;
    QString command;

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
    char *app_output_buffer;

public:
    explicit Worker(QObject *parent = nullptr);
    ~Worker();

    void makeError(QString string);

    bool setCommand(QString new_cmd);


signals:
    void signalError(QString string);

    // outputlog, loggerlog, display
    void update(QString applog, QString loggerlog, QString display, QString blindmode_display);
    void metProcess(bool met);
    void metREPL(bool met, int sharedregion_ptr);

    void sentCommand(QString cmd);
};

#endif // WORKER_H
