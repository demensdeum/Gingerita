//
// Description: Widget that local variables of the gdb inferior
//
// SPDX-FileCopyrightText: 2010 Kåre Särs <kare.sars@iki.fi>
//
//  SPDX-License-Identifier: LGPL-2.0-only

#pragma once

#include <QTreeWidget>
#include <QTreeWidgetItem>

namespace dap
{
struct Variable;
}

class LocalsView : public QTreeWidget
{
    Q_OBJECT
public:
    enum Role {
        VariableReference = Qt::UserRole + 1,
    };
    enum Type {
        PendingDataItem = QTreeWidgetItem::UserType + 1
    };
    enum Column {
        Column_Symbol = 0,
        Column_Type = 1,
        Column_Value = 2,
    };

    LocalsView(QWidget *parent = nullptr);
    ~LocalsView() override;

public Q_SLOTS:
    // An empty value string ends the locals
    void openVariableScope();
    void closeVariableScope();
    void addVariableLevel(int parentId, const dap::Variable &variable);

Q_SIGNALS:
    void localsVisible(bool visible);
    void requestVariable(int variableReference);

protected:
    void showEvent(QShowEvent *event) override;
    void hideEvent(QHideEvent *event) override;

private:
    QTreeWidgetItem *createWrappedItem(QTreeWidgetItem *parent, const dap::Variable &variable);
    QTreeWidgetItem *createWrappedItem(QTreeWidget *parent, const dap::Variable &variable);
    void onContextMenu(QPoint pos);
    void onItemExpanded(QTreeWidgetItem *);

    QHash<int, QTreeWidgetItem *> m_variables;
};
