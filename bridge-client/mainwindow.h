#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QLabel>
#include <QStringListModel>

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
    void updateAppOutput(QString);
    void updateAppStack(QStringList);
    void updateLoggerLog(QString);
    void updateBlindModeDisplay(QString);
    void updateGameText(QString);
    void updateProfileNames(QStringList);
    void updateProfiles(QVector<uint>, QVector<uint>, QVector<uint>);

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

    QStringListModel *appstack_model;
};
#endif // MAINWINDOW_H
