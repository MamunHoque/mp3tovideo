/**
 * @file MainWindow.h
 * @brief Main application window
 */

#pragma once

#include <QMainWindow>
#include <QPushButton>
#include <QLabel>
#include <QLineEdit>
#include <QComboBox>
#include <QProgressBar>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QFileDialog>
#include <QMessageBox>
#include <memory>
#include <string>
#include "audio/AudioProcessor.h"
#include "video/VideoGenerator.h"

namespace GUI {

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void browseAudioFile();
    void browseOutputFile();
    void browseBackgroundFile();
    void generateVideo();
    void updateProgress(int percent, const std::string& status);

private:
    void setupUI();
    void connectSignals();
    
    // UI Components
    QWidget* centralWidget;
    QVBoxLayout* mainLayout;
    
    // File selection
    QPushButton* browseAudioButton;
    QLineEdit* audioPathEdit;
    QPushButton* browseOutputButton;
    QLineEdit* outputPathEdit;
    QPushButton* browseBackgroundButton;
    QLineEdit* backgroundPathEdit;
    
    // Settings
    QComboBox* visualizerStyleCombo;
    QComboBox* qualityPresetCombo;
    QComboBox* backgroundTypeCombo;
    
    // Control buttons
    QPushButton* generateButton;
    QProgressBar* progressBar;
    QLabel* statusLabel;
    
    // Data
    std::unique_ptr<Audio::AudioProcessor> audioProcessor;
    std::unique_ptr<Video::VideoGenerator> videoGenerator;
};

} // namespace GUI
