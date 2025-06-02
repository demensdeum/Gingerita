/*
    SPDX-FileCopyrightText: 2019 Mark Nauwelaerts <mark.nauwelaerts@gmail.com>

    SPDX-License-Identifier: MIT
*/

#pragma once

#include <KTextEditor/ConfigPage>

class LSPClientPlugin;
struct LSPClientPluginOptions;

namespace Ui
{
class LspConfigWidget;
}

class LSPClientConfigPage : public KTextEditor::ConfigPage
{
public:
    explicit LSPClientConfigPage(QWidget *parent = nullptr, LSPClientPlugin *plugin = nullptr);
    ~LSPClientConfigPage() override;

    QString name() const override;
    QString fullName() const override;
    QIcon icon() const override;

public:
    void apply() override;
    void defaults() override;
    void reset() override;
    void configTextChanged();
    void configUrlChanged();
    void updateHighlighters();
    void showContextMenuAllowedBlocked(const QPoint &pos);

private:
    void resetUiTo(const LSPClientPluginOptions &options);

    void readUserConfig(const QString &fileName);
    void updateConfigTextErrorState();

    Ui::LspConfigWidget *ui;
    LSPClientPlugin *m_plugin;
};
