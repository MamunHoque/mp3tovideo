/**
 * @file PreviewWidget.cpp
 * @brief Implementation of preview widget
 */

#include "gui/PreviewWidget.h"
#include <QVBoxLayout>
#include <QImage>
#include <QPixmap>

namespace GUI {

PreviewWidget::PreviewWidget(QWidget *parent)
    : QWidget(parent)
{
    QVBoxLayout* layout = new QVBoxLayout(this);
    previewLabel = new QLabel(this);
    previewLabel->setAlignment(Qt::AlignCenter);
    previewLabel->setText("Preview");
    layout->addWidget(previewLabel);
}

void PreviewWidget::updatePreview(const cv::Mat& frame) {
    if (frame.empty()) {
        return;
    }
    
    cv::Mat rgb;
    cv::cvtColor(frame, rgb, cv::COLOR_RGB2BGR);
    
    QImage img(rgb.data, rgb.cols, rgb.rows, rgb.step, QImage::Format_RGB888);
    QPixmap pixmap = QPixmap::fromImage(img);
    
    // Scale to fit widget
    pixmap = pixmap.scaled(previewLabel->size(), Qt::KeepAspectRatio, Qt::SmoothTransformation);
    previewLabel->setPixmap(pixmap);
}

} // namespace GUI
