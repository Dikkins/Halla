// Native Russian Qt translation add-on for Halla Desktop v1.1.37.
// No network, audio hooks, process enumeration, or Steam integration.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <QCoreApplication>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QHash>
#include <QJsonDocument>
#include <QJsonObject>
#include <QString>
#include <QTranslator>
#include <memory>
#include <iterator>
#include "halla_plugin_api.h"

namespace {
HMODULE g_module = nullptr;
QTranslator* g_translator = nullptr;

class RussianTranslator final : public QTranslator {
public:
    bool loadTranslations(const QString& path) {
        QFile file(path);
        if (!file.open(QIODevice::ReadOnly) || file.size() > 2 * 1024 * 1024)
            return false;
        QJsonParseError error{};
        const auto doc = QJsonDocument::fromJson(file.readAll(), &error);
        if (error.error != QJsonParseError::NoError || !doc.isObject())
            return false;
        const auto table = doc.object();
        for (auto it = table.constBegin(); it != table.constEnd(); ++it) {
            if (it.value().isString() && !it.value().toString().isEmpty())
                m_text.insert(it.key(), it.value().toString());
        }
        return !m_text.isEmpty();
    }

    bool isEmpty() const override { return m_text.isEmpty(); }

    QString translate(const char* context, const char* sourceText,
                      const char* disambiguation = nullptr, int n = -1) const override {
        Q_UNUSED(context);
        Q_UNUSED(disambiguation);
        Q_UNUSED(n);
        if (!sourceText) return QString();
        const auto it = m_text.constFind(QString::fromUtf8(sourceText));
        return it == m_text.cend() ? QString() : it.value();
    }
private:
    QHash<QString, QString> m_text;
};

QString dictionaryPath() {
    wchar_t filename[32768]{};
    const DWORD copied = GetModuleFileNameW(g_module, filename, DWORD(std::size(filename)));
    if (copied == 0 || copied >= std::size(filename)) return {};
    const QFileInfo dll(QString::fromWCharArray(filename, int(copied)));
    return QDir(dll.absolutePath()).filePath(QStringLiteral("../../assets/halla_ru.json"));
}

int initializeAddon(const HallaHostApi* host) {
    if (g_translator) return 1;
    if (!host || host->abi_version != HALLA_PLUGIN_ABI_VERSION
        || host->struct_size < HALLA_HOST_API_BASE_SIZE
        || !QCoreApplication::instance()) return 0;
    auto translator = std::make_unique<RussianTranslator>();
    if (!translator->loadTranslations(dictionaryPath())) {
        if (host->log) host->log(host->context, HALLA_PLUGIN_LOG_ERROR,
                                 "RU: local translation dictionary not found");
        return 0;
    }
    if (!QCoreApplication::installTranslator(translator.get())) return 0;
    g_translator = translator.release();
    if (host->log) host->log(host->context, HALLA_PLUGIN_LOG_INFO,
                             "RU: translator installed, restart for full UI translation");
    return 1;
}

void shutdownAddon() {
    if (!g_translator) return;
    QCoreApplication::removeTranslator(g_translator);
    delete g_translator;
    g_translator = nullptr;
}

const HallaPluginApi pluginApi {
    HALLA_PLUGIN_ABI_VERSION,
    uint32_t(sizeof(HallaPluginApi)),
    "local.halla-ru",
    "Halla RU",
    "0.2.0",
    "Halla RU Community",
    "Russian Qt interface translations for Halla Desktop",
    &initializeAddon,
    &shutdownAddon,
    nullptr,
    nullptr
};
} // namespace

extern "C" HALLA_PLUGIN_EXPORT const HallaPluginApi* halla_plugin_entry() {
    return &pluginApi;
}
BOOL APIENTRY DllMain(HMODULE module, DWORD reason, LPVOID) {
    if (reason == DLL_PROCESS_ATTACH) {
        g_module = module;
        DisableThreadLibraryCalls(module);
    }
    return TRUE;
}
