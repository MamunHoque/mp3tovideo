/**
 * @file SettingsManager.h
 * @brief Settings persistence manager
 */

#pragma once

#include <QSettings>
#include <QVariant>
#include <string>

namespace GUI {

class SettingsManager {
public:
    static SettingsManager& instance();
    
    void saveAudioPath(const std::string& path);
    std::string loadAudioPath();
    
    void saveOutputPath(const std::string& path);
    std::string loadOutputPath();
    
    void saveSettings(const std::string& key, const QVariant& value);
    QVariant loadSettings(const std::string& key, const QVariant& defaultValue = QVariant());

private:
    SettingsManager();
    QSettings settings;
};

} // namespace GUI
