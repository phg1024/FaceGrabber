#include "imagewidget.h"

ImageWidget::ImageWidget()
  : isInteractive(false) {
  setSizePolicy(QSizePolicy::Fixed, QSizePolicy::Fixed);

  initializeBuffer();
  initializePen();

  setMouseTracking(true);
}

void ImageWidget::paintEvent(QPaintEvent *event) {
  QPainter painter(this);
  painter.setRenderHint(QPainter::Antialiasing, true);
  painter.fillRect(0, 0, width(), height(), Qt::white);

  if (image.width() && image.height()) {
    painter.drawImage(QRect(0, 0, width(), height()),
                      image,
                      QRect(0, 0, image.width(), image.height()));
  }

  if (isInteractive) {
    painter.setOpacity(0.5);
    painter.drawImage(QRect(0, 0, width(), height()),
                      buffer,
                      QRect(0, 0, buffer.width(), buffer.height()));

    painter.setBrush(Qt::NoBrush);
    painter.setPen(Qt::red);
    painter.drawEllipse(penPosition, pen.width()*0.5, pen.width()*0.5);
  }
}

void ImageWidget::mousePressEvent(QMouseEvent *event) {
  if (isInteractive) {
    bufferChanged = true;

    auto buttons = event->buttons();
    if (buttons & Qt::LeftButton) {
      cout << "Pressed @ ";
      cout << event->x() << ", " << event->y() << endl;
      pathPoints.clear();
      pen.setColor(Qt::black);
    } else if (buttons & Qt::RightButton) {
      pen.setColor(Qt::white);
      pathPoints.clear();
    }
  }
}

void ImageWidget::mouseReleaseEvent(QMouseEvent *event) {
  if (isInteractive) {
    cout << "Released @ ";
    cout << event->x() << ", " << event->y() << endl;
    pathPoints.clear();
  }
}

void ImageWidget::mouseMoveEvent(QMouseEvent *event) {
  if (isInteractive) {
    auto buttons = event->buttons();
    penPosition = event->pos();

    if (buttons & Qt::LeftButton || buttons & Qt::RightButton) {
      cout << event->x() << ", " << event->y() << endl;
      pathPoints.push_back(event->pos());
      paintBuffer();
    }

    repaint();
  }
}

void ImageWidget::wheelEvent(QWheelEvent *event)
{
  const int DELTA_STEP = 120;
  cout << event->delta() << endl;
  pen.setWidth(max(1, pen.width() + event->delta() / DELTA_STEP));
  repaint();
}

void ImageWidget::initializeBuffer() {
  buffer = QImage(512, 512, QImage::Format_ARGB32);

  QPainter painter(&buffer);
  painter.setRenderHint(QPainter::Antialiasing, true);
  painter.fillRect(0, 0, buffer.width(), buffer.height(), Qt::black);
}

void ImageWidget::initializePen() {
  pen = QPen(Qt::black, 5, Qt::SolidLine, Qt::RoundCap, Qt::RoundJoin);
}

void ImageWidget::paintBuffer() {
  QPainter painter(&buffer);

  painter.setBrush(Qt::white);

  if (pathPoints.empty()) return;

  QPainterPath path;

  auto& p0 = pathPoints.front();
  path.moveTo(p0.x(), p0.y());

  for (auto& p : pathPoints) {
    path.lineTo(p.x(), p.y());
  }

  painter.setPen(pen);
  painter.setBrush(Qt::NoBrush);
  painter.drawPath(path);

  //buffer.save("buffer.png");

  emit bufferUpdated(buffer);
}
