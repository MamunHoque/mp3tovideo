/**
 * @file main.cpp
 * @brief Main entry point for MP3 Spectrum Visualizer
 */

#include <QApplication>
#include <QMainWindow>
#include <QMenuBar>
#include <QStatusBar>
#include <QFileDialog>
#include <QMessageBox>
#include <iostream>
#include "gui/MainWindow.h"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    app.setApplicationName("MP3 Spectrum Visualizer");
    app.setApplicationVersion("1.0.0");
    
    GUI::MainWindow window;
    window.show();
    
    return app.exec();
}
