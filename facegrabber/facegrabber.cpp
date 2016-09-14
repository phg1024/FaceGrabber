#include "facegrabber.h"

#include <QtWidgets>
#include <QHBoxLayout>
#include <QFileInfo>
#include <QSpacerItem>

#include <fstream>
using namespace std;

FaceGrabber::FaceGrabber() : currentImageIndex(-1) {
  prevButton = new QPushButton("Previous");
  nextButton = new QPushButton("Next");

  QHBoxLayout *buttons = new QHBoxLayout();
  buttons->addSpacerItem(new QSpacerItem(20, 20, QSizePolicy::Expanding));
  buttons->addWidget(prevButton);
  buttons->addWidget(nextButton);
  buttons->addSpacerItem(new QSpacerItem(20, 20, QSizePolicy::Expanding));

  imgWidget = new ImageWidget();
  operWidget = new ImageWidget();
  maskWidget = new ImageWidget();

  QHBoxLayout *widgets = new QHBoxLayout();
  widgets->addWidget(imgWidget);
  widgets->addWidget(operWidget);
  widgets->addWidget(maskWidget);

  QVBoxLayout *layout = new QVBoxLayout();
  layout->addLayout(widgets);
  layout->addLayout(buttons);

  setLayout(layout);

  operWidget->setInteractive(true);

  connectComponents();

  setWindowTitle("Face Grabber");
}

void FaceGrabber::setInputFile(const string &filename)
{
  ifstream fin(filename);
  if(!fin) {
    cout << "Failed to open file " << filename << endl;
    exit(1);
  }

  while(fin) {
    string line;
    getline(fin, line);
    cout << line << endl;
    if (line.empty()) continue;
    filenames.push_back(line);
  }

  currentImageIndex = filenames.empty()?-1:0;

  setCurrentImage(currentImageIndex);
}

void FaceGrabber::connectComponents()
{
  connect(operWidget,
          SIGNAL(bufferUpdated(const QImage&)),
          maskWidget,
          SLOT(bindImage(const QImage&)));

  connect(prevButton,
          SIGNAL(clicked(bool)),
          this,
          SLOT(updateCurrentImage()));

  connect(nextButton,
          SIGNAL(clicked(bool)),
          this,
          SLOT(updateCurrentImage()));
}

void FaceGrabber::updateCurrentImage() {
  saveCurrentMask();

  if (sender() == prevButton) {
    --currentImageIndex;
    if (currentImageIndex < 0)  currentImageIndex += filenames.size();
  } else {
    ++currentImageIndex;
    if (currentImageIndex >= filenames.size()) currentImageIndex -= filenames.size();
  }

  setCurrentImage(currentImageIndex);
}

void FaceGrabber::saveCurrentMask() {
  QImage img(filenames[currentImageIndex].c_str());
  QFileInfo info(filenames[currentImageIndex].c_str());

  QString path = info.path();
  cout << path.toStdString() << endl;
  cout << info.baseName().toStdString() << endl;
  QString maskFilename = info.baseName() + "_mask0." + info.suffix();
  cout << maskFilename.toStdString() << endl;

  QImage mask(path + "/" + maskFilename);

  QImage newMask = operWidget->getMask().scaled(mask.width(), mask.height(), Qt::KeepAspectRatio);
  newMask.save(path + "/" + maskFilename);
}

void FaceGrabber::setCurrentImage(int idx)
{
  QImage img(filenames[idx].c_str());
  QFileInfo info(filenames[idx].c_str());

  QString path = info.path();
  cout << path.toStdString() << endl;
  cout << info.baseName().toStdString() << endl;
  QString maskFilename = info.baseName() + "_mask0." + info.suffix();
  cout << maskFilename.toStdString() << endl;

  QImage mask(path + "/" + maskFilename);

  imgWidget->bindImage(img);
  operWidget->bindImage(img);
  operWidget->bindMask(mask);
  maskWidget->bindImage(mask);
}
