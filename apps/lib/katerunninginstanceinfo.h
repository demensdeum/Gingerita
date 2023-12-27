/*
    SPDX-FileCopyrightText: 2009 Joseph Wenninger <jowenn@kde.org>

    SPDX-License-Identifier: LGPL-2.0-or-later
*/

#pragma once

#include "kateprivate_export.h"

#include <QDBusConnection>
#include <QDBusInterface>
#include <QVariant>

#include <memory>
#include <vector>

class KateRunningInstanceInfo
{
public:
    KateRunningInstanceInfo() = default;

    explicit KateRunningInstanceInfo(const QString &serviceName_)
        : valid(false)
        , serviceName(serviceName_)
        , dbus_if(new QDBusInterface(serviceName_,
                                     QStringLiteral("/MainApplication"),
                                     QString(), // I don't know why it does not work if I specify org.kde.Kate.Application here
                                     QDBusConnection::sessionBus()))
    {
        if (!dbus_if->isValid()) {
            fprintf(stderr, "%s\n", qPrintable(QDBusConnection::sessionBus().lastError().message()));
        }
        QVariant a_s = dbus_if->property("activeSession");
        /*      std::cerr<<a_s.isValid()<<std::endl;
              std::cerr<<"property:"<<qPrintable(a_s.toString())<<std::endl;
              std::cerr<<qPrintable(QDBusConnection::sessionBus().lastError().message())<<std::endl;*/
        if (!a_s.isValid()) {
            sessionName = QStringLiteral("___NO_SESSION_OPENED__%1").arg(dummy_session++);
            valid = false;
        } else {
            if (a_s.toString().isEmpty()) {
                sessionName = QStringLiteral("___DEFAULT_CONSTRUCTED_SESSION__%1").arg(dummy_session++);
            } else {
                sessionName = a_s.toString();
            }
            valid = true;
        }
    }

    bool valid = false;
    const QString serviceName;
    std::unique_ptr<QDBusInterface> dbus_if;
    QString sessionName;

private:
    static inline int dummy_session = 0;
};

KATE_PRIVATE_EXPORT std::vector<KateRunningInstanceInfo> fillinRunningKateAppInstances();
