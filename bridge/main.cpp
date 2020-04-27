#include "mainwindow.h"
#include "worker.h"

#include <QApplication>

#include <QDebug>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    MainWindow w;
    if (w.initialize() == false) {
        return 0;
    }

    Worker worker;
    QObject::connect(&worker, SIGNAL(update(QString, QString, QString)),
                     &w, SLOT(update(QString, QString, QString)),
                     Qt::QueuedConnection);
    QObject::connect(&worker, SIGNAL(metProcess(bool)),
                     &w, SLOT(metProcess(bool)),
                     Qt::QueuedConnection);
    QObject::connect(&worker, SIGNAL(metREPL(bool)),
                     &w, SLOT(metREPL(bool)),
                     Qt::QueuedConnection);
    QObject::connect(&worker, SIGNAL(signalError(QString)),
                     &w, SLOT(setError(QString)),
                     Qt::QueuedConnection);

    worker.start();
    w.show();
    a.exec();
    worker.requestInterruption();
    worker.wait();
    return 0;
}
