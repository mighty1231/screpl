#include "mainwindow.h"
#include "ui_mainwindow.h"

#include <Windows.h>
#include <QDebug>
#include <QTextCursor>
#include <QFileDialog>
#include <QSaveFile>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow), worker(NULL),
      string_found("<font color=#10FF10>found</font>"),
      string_notfound("<font color=#FF1010>not found</font>")
{
    ui->setupUi(this);

    label_proc = new QLabel(QString("Starcraft %1").arg(string_notfound));
    label_repl= new QLabel(QString("REPL %1").arg(string_notfound));
    ui->statusbar->addPermanentWidget(label_proc);
    ui->statusbar->addPermanentWidget(label_repl);

    ui->from_profiletable->setHorizontalHeaderLabels(QStringList()
                                                     << tr("Count")
                                                     << tr("Consumed[ms]")
                                                     << tr("Expected[ms]")
                                                     << tr("AvgCon[ms]")
                                                     << tr("AvgExp[ms]"));
    appstack_model = new QStringListModel(this);
    ui->appstacklistview->setModel(appstack_model);

    connect(ui->from_dumpbtn, SIGNAL(clicked()), this, SLOT(dumpOutput()));
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
    worker->setConnection(this);

    connect(ui->sendcmdbtn, SIGNAL(clicked()),
            this, SLOT(tryCommand()));
    return true;
}

void MainWindow::updateAppOutput(QString app_output)
{
    if (app_output.isEmpty())
        return;
    QTextCursor prev_cursor = ui->from_appoutput->textCursor();
    ui->from_appoutput->moveCursor(QTextCursor::End);
    ui->from_appoutput->insertPlainText(app_output);
    ui->from_appoutput->moveCursor(QTextCursor::End);
    if (prev_cursor.atEnd())
        ui->from_appoutput->moveCursor(QTextCursor::End);
    else
        ui->from_appoutput->setTextCursor(prev_cursor);
}

void MainWindow::updateAppStack(QStringList new_appnames)
{
    QStringList prev = appstack_model->stringList();
    QStringList update;

    // if differs, update model
    bool changed = false;

    QStringList::reverse_iterator new_it = new_appnames.rbegin();
    while (new_it != new_appnames.crend()) {
        update << *new_it;
        new_it++;
    }

    if (prev.size() != update.size()) {
        changed = true;
    } else {
        QStringList::iterator prev_it = prev.begin();
        QStringList::iterator update_it = update.begin();
        while (prev_it != prev.end()) {
            if (prev_it->compare(*update_it)) {
                changed = true;
                break;
            }

            prev_it++;
            update_it++;
        }
    }
    if (changed) {
        ui->appstacklistview->setCurrentIndex(appstack_model->index(0));
        appstack_model->setStringList(update);
    }
}

void MainWindow::updateLoggerLog(QString logger_log)
{
    if (logger_log.isEmpty())
        return;
    QTextCursor prev_cursor = ui->from_logger->textCursor();
    ui->from_logger->moveCursor(QTextCursor::End);
    ui->from_logger->insertPlainText(logger_log);
    if (prev_cursor.atEnd())
        ui->from_logger->moveCursor(QTextCursor::End);
    else
        ui->from_logger->setTextCursor(prev_cursor);
}

void MainWindow::updateBlindModeDisplay(QString blindmode_text)
{
    QString prev = ui->from_blindmodedisplay->toPlainText();
    if (prev.compare(blindmode_text)) {
        ui->from_blindmodedisplay->setText(blindmode_text);
    }
}

void MainWindow::updateGameText(QString text)
{
    QString prev = ui->from_display->toPlainText();
    if (prev.compare(text)) {
        ui->from_display->setText(text);
    }
}

void MainWindow::updateProfileNames(QStringList names)
{
    ui->from_profiletable->setRowCount(names.length());
    ui->from_profiletable->setVerticalHeaderLabels(names);
}

void MainWindow::updateProfiles(QVector<uint> counter, QVector<uint> total_ms, QVector<uint> total_ems)
{
    QTableWidgetItem *pCell;
    for (int i=0; i<total_ms.size(); i++) {
        int _counter = counter.at(i);
        int _total_ms = total_ms.at(i);
        int _total_ems = total_ems.at(i);

        pCell = ui->from_profiletable->item(i, 0);
        if(!pCell) {
            pCell = new QTableWidgetItem();
            pCell->setTextAlignment(Qt::AlignRight);
            ui->from_profiletable->setItem(i, 0, pCell);
        }
        pCell->setText(QString::number(_counter));

        pCell = ui->from_profiletable->item(i, 1);
        if(!pCell) {
            pCell = new QTableWidgetItem();
            pCell->setTextAlignment(Qt::AlignRight);
            ui->from_profiletable->setItem(i, 1, pCell);
        }
        pCell->setText(QString::number(_total_ms));

        pCell = ui->from_profiletable->item(i, 2);
        if(!pCell) {
            pCell = new QTableWidgetItem();
            pCell->setTextAlignment(Qt::AlignRight);
            ui->from_profiletable->setItem(i, 2, pCell);
        }
        pCell->setText(QString::number(_total_ems));

        pCell = ui->from_profiletable->item(i, 3);
        if(!pCell) {
            pCell = new QTableWidgetItem();
            pCell->setTextAlignment(Qt::AlignRight);
            ui->from_profiletable->setItem(i, 3, pCell);
        }
        if (_counter == 0) {
            pCell->setText("N/A");
        } else {
            double average = ((double)_total_ms) / _counter;
            pCell->setText(QString("%1").arg(average, 0, 'f', 1, '0'));
        }

        pCell = ui->from_profiletable->item(i, 4);
        if(!pCell) {
            pCell = new QTableWidgetItem();
            pCell->setTextAlignment(Qt::AlignRight);
            ui->from_profiletable->setItem(i, 4, pCell);
        }
        if (_counter == 0) {
            pCell->setText("N/A");
        } else {
            double average = ((double)_total_ems) / _counter;
            pCell->setText(QString("%1").arg(average, 0, 'f', 1, '0'));
        }
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

void MainWindow::metREPL(bool met, int sharedregion_ptr)
{
    if (met) {
        ui->statusbar->showMessage("REPL found!", 4000);
        ui->sendcmdbtn->setEnabled(true);
        ui->label_sharedregion->setText(QString::asprintf("SharedRegion on 0x%08X", sharedregion_ptr));
        label_repl->setText(QString("REPL %1").arg(string_found));
    } else {
        ui->statusbar->showMessage("REPL lost", 4000);
        ui->sendcmdbtn->setEnabled(false);
        ui->label_sharedregion->setText("SharedRegion");
        label_repl->setText(QString("REPL %1").arg(string_notfound));
    }
}

void MainWindow::setError(QString msg)
{
    qDebug() << "error" << msg;
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

void MainWindow::dumpOutput()
{
    QString text = ui->from_appoutput->textCursor().selectedText();
    QString fileName = QFileDialog::getSaveFileName(this,
        tr("Save Dump file"), "",
        tr("All Files (*)"));
    if (fileName.isEmpty())
        return;
    else {
        QSaveFile file(fileName);
        if (!file.open(QIODevice::WriteOnly)) {
            return;
        }
        file.write(QByteArray::fromHex(text.toLatin1()));
        file.commit();
    }
}
