#include "mainwindow.h"
#include "ui_mainwindow.h"

#include <Windows.h>
#include <QDebug>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);
}

MainWindow::~MainWindow()
{
    delete ui;
}

bool MainWindow::initialize() {
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

    return true;
}

void MainWindow::update(QString applog, QString loggerlog, QString display)
{
    ui->from_log->append(applog);
    ui->from_logger->append(loggerlog);

    QString prev = ui->from_display->toPlainText();
    if (prev.compare(display)) {
        ui->from_display->setText(display);
    }
}

void MainWindow::metProcess(bool met)
{
    qDebug() << "metProcess " << met;
}

void MainWindow::metREPL(bool met)
{
    qDebug() << "metREPL " << met;
}

void MainWindow::setError(QString msg)
{
    ui->statuslabel->setText(msg);
}
