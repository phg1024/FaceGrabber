#include "imagewidget.h"
#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"

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
    painter.setOpacity(0.25);
    painter.drawImage(QRect(0, 0, width(), height()),
                      buffer,
                      QRect(0, 0, buffer.width(), buffer.height()));


    painter.setOpacity(0.25);
    painter.drawImage(QRect(0, 0, width(), height()),
                      refinementBuffer,
                      QRect(0, 0, refinementBuffer.width(), refinementBuffer.height()));

    painter.drawImage(QRect(0, 0, width(), height()),
                      classificationBuffer,
                      QRect(0, 0, classificationBuffer.width(), classificationBuffer.height()));

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

    if (event->modifiers() & Qt::ControlModifier) {
      cout << "Refining painted region" << endl;

      refinePaintedRegion();
    }

    repaint();
  }
}

void ImageWidget::mouseMoveEvent(QMouseEvent *event) {
  if (isInteractive) {
    auto buttons = event->buttons();
    penPosition = event->pos();

    if (buttons & Qt::LeftButton || buttons & Qt::RightButton) {
      cout << event->x() << ", " << event->y() << endl;
      pathPoints.push_back(event->pos());

      if (event->modifiers() & Qt::ControlModifier) {
        cout << "Refining region" << endl;
        paintRefinementBuffer();
      } else {
        paintBuffer();
      }
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

void ImageWidget::keyPressEvent(QKeyEvent *event)
{
  switch(event->key()) {
  case Qt::Key_F: {
    cout << "Flipping refinement ..." << endl;
    flipRefinement();
    repaint();
    break;
  }
  case Qt::Key_Space: {
    cout << "Applying refinement ..." << endl;
    applyRefinement();
    repaint();
    break;
  }
  default: {
    cout << "Key pressed." << endl;
    break;
  }
  }
}

void ImageWidget::enterEvent(QEvent *event)
{
  setFocus();
}

void ImageWidget::leaveEvent(QEvent *event)
{
  clearFocus();
}

void ImageWidget::clearBuffer(QImage& buf, QColor c) {
  QPainter painter(&buf);
  painter.setRenderHint(QPainter::Antialiasing, true);
  painter.fillRect(0, 0, buf.width(), buf.height(), Qt::black);
  painter.fillRect(0, 0, buf.width(), buf.height(), c);
}

void ImageWidget::initializeBuffer() {
  buffer = QImage(512, 512, QImage::Format_ARGB32);
  clearBuffer(buffer);

  refinementBuffer = QImage(512, 512, QImage::Format_ARGB32);
  clearBuffer(refinementBuffer);

  classificationBuffer = QImage(512, 512, QImage::Format_ARGB32);
  clearBuffer(classificationBuffer, QColor(0, 0, 0, 0));
}

void ImageWidget::initializePen() {
  pen = QPen(Qt::black, 5, Qt::SolidLine, Qt::RoundCap, Qt::RoundJoin);
}

void ImageWidget::paintRefinementBuffer() {
  QPainter painter(&refinementBuffer);

  painter.setBrush(Qt::red);

  if (pathPoints.empty()) return;

  QPainterPath path;

  auto& p0 = pathPoints.front();
  path.moveTo(p0.x(), p0.y());

  for (auto& p : pathPoints) {
    path.lineTo(p.x(), p.y());
  }

  QColor c = pen.color();
  pen.setColor(Qt::red);

  painter.setPen(pen);
  painter.setBrush(Qt::NoBrush);
  painter.drawPath(path);

  pen.setColor(c);
}

namespace {
struct pixel_t {
  pixel_t() {}
  pixel_t(int x, int y, QRgb p) :
    x(x), y(y) {
    tie(r, g, b) = unpack_qrgb(p);
  }

  pixel_t(int x, int y, int r, int g, int b) :
    x(x), y(y), r(r), g(g), b(b) {}

  static tuple<int, int, int> unpack_qrgb(QRgb p) {
    int r = qRed(p);
    int g = qGreen(p);
    int b = qBlue(p);
    return make_tuple(r, g, b);
  }

  int x, y;
  int r, g, b;
};
}

void ImageWidget::refinePaintedRegion()
{
  clearBuffer(classificationBuffer, QColor(0, 0, 0, 0));

  // get all pixels in the painted region
  vector<pixel_t> all_pixels;
  for (int y=0;y<refinementBuffer.height();++y) {
    for(int x=0; x<refinementBuffer.width();++x) {
      auto pix = refinementBuffer.pixel(x, y);
      int r, g, b;
      tie(r, g, b) = pixel_t::unpack_qrgb(pix);

      if (r == 0 && g == 0 && b == 0) continue;

      all_pixels.push_back(pixel_t(x, y, image.pixel(x*0.5, y*0.5)));
    }
  }

  cout << "num pixels = " << all_pixels.size() << endl;

  // classify the pixels in the painted region
  cv::Mat p = cv::Mat::zeros(all_pixels.size(), 3, CV_32F);
  for (int i=0;i<all_pixels.size();++i) {
    p.at<float>(i, 0) = all_pixels[i].r / 255.0;
    p.at<float>(i, 1) = all_pixels[i].g / 255.0;
    p.at<float>(i, 2) = all_pixels[i].b / 255.0;
    //p.at<float>(i, 3) = all_pixels[i].x / 512.0;
    //p.at<float>(i, 4) = all_pixels[i].y / 512.0;
  }

  cv::Mat bestLabels, centers;
  cv::kmeans(p, 2, bestLabels,
             cv::TermCriteria(CV_TERMCRIT_EPS+CV_TERMCRIT_ITER, 10, 1.0),
             3, cv::KMEANS_PP_CENTERS, centers);

  // show the classification in the classification buffer
  for(int i=0;i<all_pixels.size();++i) {
    int cls_idx = bestLabels.at<int>(0,i);
    if (cls_idx) {
      classificationBuffer.setPixel(all_pixels[i].x, all_pixels[i].y, qRgba(0, 255, 0, 180));
    } else {
      classificationBuffer.setPixel(all_pixels[i].x, all_pixels[i].y, qRgba(255, 255, 0, 180));
    }
  }

  // clear refinement buffer
  clearBuffer(refinementBuffer);
}

void ImageWidget::flipRefinement()
{
  for (int y=0;y<classificationBuffer.height();++y) {
    for(int x=0; x<classificationBuffer.width();++x) {
      auto pix = classificationBuffer.pixel(x, y);

      int r, g, b;
      tie(r, g, b) = pixel_t::unpack_qrgb(pix);

      if (r == 0 && g == 0 && b == 0) continue;

      if (r == 0) {
        classificationBuffer.setPixel(x, y, qRgba(255, 255, 0, 180));
      } else {
        classificationBuffer.setPixel(x, y, qRgba(0, 255, 0, 180));
      }
    }
  }
}

void ImageWidget::applyRefinement()
{
  for (int y=0;y<classificationBuffer.height();++y) {
    for(int x=0; x<classificationBuffer.width();++x) {
      auto pix = classificationBuffer.pixel(x, y);

      int r, g, b;
      tie(r, g, b) = pixel_t::unpack_qrgb(pix);

      if (r == 0 && g == 0 && b == 0) continue;

      if (r == 0) {
        cout << "set to white" << endl;
        // blue -> 1
        buffer.setPixel(x, y, qRgb(255, 255, 255));
      } else {
        cout << "set to black" << endl;
        // yellow -> 0
        buffer.setPixel(x, y, qRgb(0, 0, 0));
      }
    }
  }

  emit bufferUpdated(buffer);
  clearBuffer(classificationBuffer, QColor(0, 0, 0, 0));
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
