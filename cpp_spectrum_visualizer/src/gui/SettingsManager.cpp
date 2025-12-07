/**
 * @file SettingsManager.cpp
 * @brief Implementation of settings manager
 */

#include "gui/SettingsManager.h"
#include <QVariant>

namespace GUI {

SettingsManager::SettingsManager()
    : settings("SpectrumVisualizer", "MP3ToVideo")
{
}

SettingsManager& SettingsManager::instance() {
    static SettingsManager instance;
    return instance;
}

void SettingsManager::saveAudioPath(const std::string& path) {
    settings.setValue("audioPath", QString::fromStdString(path));
}

std::string SettingsManager::loadAudioPath() {
    return settings.value("audioPath", "").toString().toStdString();
}

void SettingsManager::saveOutputPath(const std::string& path) {
    settings.setValue("outputPath", QString::fromStdString(path));
}

std::string SettingsManager::loadOutputPath() {
    return settings.value("outputPath", "").toString().toStdString();
}

void SettingsManager::saveSettings(const std::string& key, const QVariant& value) {
    settings.setValue(QString::fromStdString(key), value);
}

QVariant SettingsManager::loadSettings(const std::string& key, const QVariant& defaultValue) {
    return settings.value(QString::fromStdString(key), defaultValue);
}

} // namespace GUI
