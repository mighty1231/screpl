#include "mainwindow.h"
#include "ui_mainwindow.h"

#include <Windows.h>
#include <QDebug>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow), worker(NULL),
      string_found("<font color=#10FF10>found</font>"),
      string_notfound("<font color=#FF1010>not found</font>")
{
    ui->setupUi(this);
    this->setWindowTitle("SC-REPL Bridge Client");

    label_proc = new QLabel(QString("Starcraft %1").arg(string_notfound));
    label_repl= new QLabel(QString("REPL %1").arg(string_notfound));
    ui->statusbar->addPermanentWidget(label_proc);
    ui->statusbar->addPermanentWidget(label_repl);
}

MainWindow::~MainWindow()
{
    delete ui;
}

bool MainWindow::initialize(Worker *_worker) {
    // previlege
    void *tokenHandle;
    OpenProcessToken( GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES , &tokenHandle );
    TOKEN_PRIVILEGES privilegeToken;
    LookupPrivilegeValue( 0, SE_DEBUG_NAME, &privilegeToken.Privileges[ 0 ].Luid );
    privilegeToken.PrivilegeCount = 1;
    privilegeToken.Privileges[ 0 ].Attributes = SE_PRIVILEGE_ENABLED;
    AdjustTokenPrivileges( tokenHandle, 0, &privilegeToken, sizeof( TOKEN_PRIVILEGES ), 0, 0 );
    if ( !CloseHandle( tokenHandle ) ){
        MessageBoxW( 0, L"Token error", L"Error", MB_ICONERROR );
        return false;
    }

    worker = _worker;
    connect(worker, SIGNAL(update(QString, QString, QString)),
            this, SLOT(update(QString, QString, QString)),
            Qt::QueuedConnection);
    connect(worker, SIGNAL(metProcess(bool)),
            this, SLOT(metProcess(bool)),
            Qt::QueuedConnection);
    connect(worker, SIGNAL(metREPL(bool)),
            this, SLOT(metREPL(bool)),
            Qt::QueuedConnection);
    connect(worker, SIGNAL(signalError(QString)),
            this, SLOT(setError(QString)),
            Qt::QueuedConnection);
    connect(worker, SIGNAL(sentCommand(QString)),
            this, SLOT(sentCommand(QString)),
            Qt::QueuedConnection);
    connect(ui->sendcmdbtn, SIGNAL(clicked()),
            this, SLOT(tryCommand()));
    return true;
}

void MainWindow::update(QString applog, QString loggerlog, QString display)
{
    if (!applog.isEmpty()) {
        ui->from_log->append(applog);
    }

    if (!loggerlog.isEmpty()) {
        ui->from_logger->append(loggerlog);
    }


    QString prev = ui->from_display->toPlainText();
    if (prev.compare(display)) {
        ui->from_display->setText(display);
    }
}

void MainWindow::metProcess(bool met)
{
    if (met) {
        ui->statusbar->showMessage("Starcraft found!", 4000);
        label_proc->setText(QString("Starcraft %1").arg(string_found));
    } else {
        ui->statusbar->showMessage("Starcraft lost", 4000);
        label_proc->setText(QString("Starcraft %1").arg(string_notfound));
    }
}

void MainWindow::metREPL(bool met)
{
    if (met) {
        ui->statusbar->showMessage("REPL found!", 4000);
        ui->sendcmdbtn->setEnabled(true);
        label_repl->setText(QString("REPL %1").arg(string_found));
    } else {
        ui->statusbar->showMessage("REPL lost", 4000);
        ui->sendcmdbtn->setEnabled(false);
        label_repl->setText(QString("REPL %1").arg(string_notfound));
    }
}

void MainWindow::setError(QString msg)
{
    ui->statusbar->showMessage(msg, 5000);
}

void MainWindow::tryCommand()
{
    QString command = ui->cmdedit->text();
    if (worker->setCommand(command)) {
        ui->sendcmdbtn->setEnabled(false);
    } else {
        setError("Sending command failed, please retry");
    }
}

void MainWindow::sentCommand(QString command)
{
    ui->statusbar->showMessage(QString("Command %1 sent!").arg(command), 5000);
    ui->to_cmdlog->append(command);
    ui->sendcmdbtn->setEnabled(true);
}
