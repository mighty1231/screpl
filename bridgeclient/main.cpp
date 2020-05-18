#include "mainwindow.h"
#include "worker.h"

#include <QApplication>

#include <QDebug>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    MainWindow w;

    Worker worker;
    if (w.initialize(&worker) == false) {
        return 0;
    }
    qDebug()<< "start!";
    worker.start();
    qDebug()<< "window!";
    w.show();
    a.exec();
    worker.requestInterruption();
    worker.wait();
    return 0;
}
