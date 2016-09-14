#ifndef FACEGRABBER_H
#define FACEGRABBER_H

#include <QPainter>
#include <QWidget>
#include <QPushButton>

#include "imagewidget.h"

class FaceGrabber : public QWidget {
  Q_OBJECT

public:
  FaceGrabber();

private slots:
  void updateCurrentImage();

public slots:
  void setInputFile(const string& filename);

protected:
  void connectComponents();

private:
  void setCurrentImage(int idx);
  void saveCurrentMask();

private:
  ImageWidget *imgWidget, *maskWidget;
  ImageWidget *operWidget;
  QPushButton *prevButton, *nextButton;

  vector<string> filenames;
  int currentImageIndex;
};

#endif  // FACEGRABBER_H
