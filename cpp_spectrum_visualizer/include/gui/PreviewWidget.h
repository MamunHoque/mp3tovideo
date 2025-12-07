/**
 * @file PreviewWidget.h
 * @brief Preview widget for video frames
 */

#pragma once

#include <QWidget>
#include <QLabel>
#include <opencv2/opencv.hpp>

namespace GUI {

class PreviewWidget : public QWidget {
    Q_OBJECT

public:
    explicit PreviewWidget(QWidget *parent = nullptr);
    void updatePreview(const cv::Mat& frame);

private:
    QLabel* previewLabel;
};

} // namespace GUI
