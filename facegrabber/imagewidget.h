#ifndef IMAGEWIDGET_H
#define IMAGEWIDGET_H

#include <QPainter>
#include <QWidget>
#include <QMouseEvent>
#include <QDebug>

#include <iostream>
using namespace std;

class ImageWidget : public QWidget {
  Q_OBJECT

public:
  ImageWidget();

  QSize sizeHint() const {
    return QSize(512, 512);
  }

  QImage getMask() const {
    return buffer;
  }

signals:
  void bufferUpdated(const QImage& img);

private slots:

public slots:
  void bindImage(const QImage& img) {
    image = img;
    repaint();
  }

  void bindMask(const QImage& mask) {
    QPainter painter(&buffer);
    painter.drawImage(QRect(0, 0, buffer.width(), buffer.height()),
                      mask,
                      QRect(0, 0, mask.width(), mask.height()));

    repaint();
  }

  void setInteractive(bool val) {
    isInteractive = val;
  }

protected:
  void paintEvent(QPaintEvent* event) Q_DECL_OVERRIDE;
  void mousePressEvent(QMouseEvent* event);
  void mouseReleaseEvent(QMouseEvent* event);
  void mouseMoveEvent(QMouseEvent* event);
  void wheelEvent(QWheelEvent* event);

private:
  void initializeBuffer();
  void initializePen();
  void paintBuffer();

private:
  QImage image;
  QImage buffer;
  bool isInteractive;

  vector<QPoint> pathPoints;
  QPen pen;
  QPoint penPosition;
};

#endif  // FACEGRABBER_H
