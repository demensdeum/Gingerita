/*
    SPDX-FileCopyrightText: 2009 Joseph Wenninger <jowenn@kde.org>

    SPDX-License-Identifier: LGPL-2.0-or-later
*/

#include "katerunninginstanceinfo.h"
#include <QCoreApplication>
#include <QDBusConnectionInterface>
#include <QDBusReply>
#include <QFileInfo>
#include <QRegularExpression>
#include <QStringList>

std::vector<KateRunningInstanceInfo> fillinRunningKateAppInstances()
{
    // if we have no dbus, nothing to do
    std::vector<KateRunningInstanceInfo> instances;
    auto i = QDBusConnection::sessionBus().interface();
    if (!i) {
        return instances;
    }

    // get all instances
    const QDBusReply<QStringList> servicesReply = i->registeredServiceNames();
    if (!servicesReply.isValid()) {
        return instances;
    }

    // try to filter out the current instance
    const bool inSandbox = QFileInfo::exists(QStringLiteral("/flatpak-info"));
    const QString my_pid = inSandbox ? QDBusConnection::sessionBus().baseService().replace(QRegularExpression(QStringLiteral("[\\.:]")), QStringLiteral("_"))
                                     : QString::number(QCoreApplication::applicationPid());
    for (const QString &s : servicesReply.value()) {
        if (s.startsWith(QLatin1String("org.kde.kate")) && !s.endsWith(my_pid)) {
            instances.emplace_back(s);
        }
    }
    return instances;
}
