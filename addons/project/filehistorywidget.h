#ifndef FILEHISTORYWIDGET_H
#define FILEHISTORYWIDGET_H

#include <QListView>
#include <QPushButton>
#include <QWidget>

class FileHistoryWidget : public QWidget
{
    Q_OBJECT
public:
    explicit FileHistoryWidget(const QString &file, QWidget *parent = nullptr);

private Q_SLOTS:
    void itemClicked(const QModelIndex &idx);

private:
    QList<QByteArray> getFileHistory(const QString &file);

    QPushButton m_backBtn;
    QListView *m_listView;
    QString m_file;

Q_SIGNALS:
    void backClicked();
    void commitClicked(const QString &file, const QByteArray &contents);
    void errorMessage(const QString &msg, bool warn);
};

#endif // FILEHISTORYWIDGET_H
