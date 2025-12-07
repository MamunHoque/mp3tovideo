/**
 * @file MainWindow.cpp
 * @brief Implementation of main window
 */

#include "gui/MainWindow.h"
#include <QThread>
#include <QApplication>
#include <QFileDialog>
#include <QMessageBox>
#include <QVariant>
#include <iostream>

namespace GUI {

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
    setupUI();
    connectSignals();
    setWindowTitle("MP3 Spectrum Visualizer");
    resize(600, 500);
}

MainWindow::~MainWindow() {
}

void MainWindow::setupUI() {
    centralWidget = new QWidget(this);
    setCentralWidget(centralWidget);
    
    mainLayout = new QVBoxLayout(centralWidget);
    
    // Audio file selection
    QHBoxLayout* audioLayout = new QHBoxLayout();
    browseAudioButton = new QPushButton("Browse Audio...", this);
    audioPathEdit = new QLineEdit(this);
    audioPathEdit->setPlaceholderText("Select audio file (MP3, WAV, etc.)");
    audioLayout->addWidget(audioPathEdit);
    audioLayout->addWidget(browseAudioButton);
    mainLayout->addLayout(audioLayout);
    
    // Output file selection
    QHBoxLayout* outputLayout = new QHBoxLayout();
    browseOutputButton = new QPushButton("Browse Output...", this);
    outputPathEdit = new QLineEdit(this);
    outputPathEdit->setPlaceholderText("Output video file path");
    outputLayout->addWidget(outputPathEdit);
    outputLayout->addWidget(browseOutputButton);
    mainLayout->addLayout(outputLayout);
    
    // Background file selection
    QHBoxLayout* bgLayout = new QHBoxLayout();
    browseBackgroundButton = new QPushButton("Browse Background...", this);
    backgroundPathEdit = new QLineEdit(this);
    backgroundPathEdit->setPlaceholderText("Background image or video (optional)");
    bgLayout->addWidget(backgroundPathEdit);
    bgLayout->addWidget(browseBackgroundButton);
    mainLayout->addLayout(bgLayout);
    
    // Visualizer style
    QHBoxLayout* styleLayout = new QHBoxLayout();
    styleLayout->addWidget(new QLabel("Visualizer Style:", this));
    visualizerStyleCombo = new QComboBox(this);
    visualizerStyleCombo->addItems({"bars", "waveform", "circle", "particle"});
    styleLayout->addWidget(visualizerStyleCombo);
    mainLayout->addLayout(styleLayout);
    
    // Quality preset
    QHBoxLayout* qualityLayout = new QHBoxLayout();
    qualityLayout->addWidget(new QLabel("Quality:", this));
    qualityPresetCombo = new QComboBox(this);
    qualityPresetCombo->addItems({"fast", "balanced", "high"});
    qualityLayout->addWidget(qualityPresetCombo);
    mainLayout->addLayout(qualityLayout);
    
    // Generate button
    generateButton = new QPushButton("Generate Video", this);
    generateButton->setStyleSheet("QPushButton { padding: 10px; font-size: 14px; }");
    mainLayout->addWidget(generateButton);
    
    // Progress bar
    progressBar = new QProgressBar(this);
    progressBar->setVisible(false);
    mainLayout->addWidget(progressBar);
    
    // Status label
    statusLabel = new QLabel("Ready", this);
    mainLayout->addWidget(statusLabel);
    
    mainLayout->addStretch();
}

void MainWindow::connectSignals() {
    connect(browseAudioButton, &QPushButton::clicked, this, &MainWindow::browseAudioFile);
    connect(browseOutputButton, &QPushButton::clicked, this, &MainWindow::browseOutputFile);
    connect(browseBackgroundButton, &QPushButton::clicked, this, &MainWindow::browseBackgroundFile);
    connect(generateButton, &QPushButton::clicked, this, &MainWindow::generateVideo);
}

void MainWindow::browseAudioFile() {
    QString path = QFileDialog::getOpenFileName(this, "Select Audio File", "",
                                                 "Audio Files (*.mp3 *.wav *.flac *.m4a)");
    if (!path.isEmpty()) {
        audioPathEdit->setText(path);
    }
}

void MainWindow::browseOutputFile() {
    QString path = QFileDialog::getSaveFileName(this, "Save Video As", "",
                                                 "Video Files (*.mp4 *.avi *.mov)");
    if (!path.isEmpty()) {
        outputPathEdit->setText(path);
    }
}

void MainWindow::browseBackgroundFile() {
    QString path = QFileDialog::getOpenFileName(this, "Select Background", "",
                                                 "Media Files (*.mp4 *.jpg *.png *.jpeg)");
    if (!path.isEmpty()) {
        backgroundPathEdit->setText(path);
    }
}

void MainWindow::generateVideo() {
    QString audioPath = audioPathEdit->text();
    QString outputPath = outputPathEdit->text();
    
    if (audioPath.isEmpty() || outputPath.isEmpty()) {
        QMessageBox::warning(this, "Error", "Please select audio and output files.");
        return;
    }
    
    // Load audio
    try {
        audioProcessor = std::make_unique<Audio::AudioProcessor>(audioPath.toStdString());
        if (!audioProcessor->loadAudio()) {
            QMessageBox::critical(this, "Error", "Failed to load audio file.");
            return;
        }
    } catch (const std::exception& e) {
        QMessageBox::critical(this, "Error", QString("Error loading audio: %1").arg(e.what()));
        return;
    }
    
    // Prepare settings
    Video::GenerationSettings settings;
    settings.width = 1920;
    settings.height = 1080;
    settings.fps = 30;
    settings.visualizerStyle = visualizerStyleCombo->currentText().toStdString();
    
    QString bgPath = backgroundPathEdit->text();
    if (!bgPath.isEmpty()) {
        if (bgPath.endsWith(".mp4", Qt::CaseInsensitive)) {
            settings.backgroundType = "video";
            settings.backgroundPath = bgPath.toStdString();
        } else {
            settings.backgroundType = "image";
            settings.backgroundPath = bgPath.toStdString();
        }
    } else {
        settings.backgroundType = "solid";
    }
    
    // Quality preset
    QString quality = qualityPresetCombo->currentText();
    if (quality == "fast") {
        settings.encodingSettings.preset = "ultrafast";
        settings.encodingSettings.bitrate = 3000000;
    } else if (quality == "high") {
        settings.encodingSettings.preset = "slow";
        settings.encodingSettings.bitrate = 8000000;
    } else {
        settings.encodingSettings.preset = "medium";
        settings.encodingSettings.bitrate = 5000000;
    }
    
    // Create generator
    try {
        videoGenerator = std::make_unique<Video::VideoGenerator>(*audioProcessor, settings);
    } catch (const std::exception& e) {
        QMessageBox::critical(this, "Error", QString("Error creating video generator: %1").arg(e.what()));
        return;
    }
    
    // For now, generate synchronously (TODO: add threading later)
    progressBar->setVisible(true);
    progressBar->setValue(0);
    statusLabel->setText("Generating video...");
    generateButton->setEnabled(false);
    QApplication::processEvents();
    
    bool success = videoGenerator->generateVideo(
        outputPath.toStdString(), 
        audioPath.toStdString(),
        [this](int percent, const std::string& status) {
            progressBar->setValue(percent);
            statusLabel->setText(QString::fromStdString(status));
            QApplication::processEvents();
        }
    );
    
    progressBar->setVisible(false);
    generateButton->setEnabled(true);
    if (success) {
        statusLabel->setText("Generation complete!");
        QMessageBox::information(this, "Success", "Video generated successfully!");
    } else {
        statusLabel->setText("Generation failed!");
        QMessageBox::critical(this, "Error", "Video generation failed. Check console for details.");
    }
}

void MainWindow::updateProgress(int percent, const std::string& status) {
    progressBar->setValue(percent);
    statusLabel->setText(QString::fromStdString(status));
    QApplication::processEvents();
}

} // namespace GUI
