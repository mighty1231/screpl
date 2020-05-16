#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QLabel>

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
    void update(QString applog, QString loggerlog, QString display, QString blindmode_display);
    void metProcess(bool met);
    void metREPL(bool met, int sharedregion_ptr);

    void setError(QString msg);

    void tryCommand();
    void sentCommand(QString command);

    void dumpOutput();

private:
    Ui::MainWindow *ui;
    Worker *worker;

    QString string_found;
    QString string_notfound;

    QLabel *label_proc;
    QLabel *label_repl;
};
#endif // MAINWINDOW_H
