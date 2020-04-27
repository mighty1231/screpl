#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include "worker.h"

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

    bool initialize(Worker *worker);

public slots:
    void update(QString applog, QString loggerlog, QString display);
    void metProcess(bool met);
    void metREPL(bool met);

    void setError(QString msg);

private:
    Ui::MainWindow *ui;
    Worker *worker;
};
#endif // MAINWINDOW_H
