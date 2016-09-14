#include <QApplication>

#include "facegrabber.h"

int main(int argc, char** argv) {
  QApplication app(argc, argv);

  if (argc > 1) {
    string filename = argv[1];
    FaceGrabber grabber;
    grabber.setInputFile(filename);
    grabber.show();
    return app.exec();
  } else {
    cout << "Usage: " << argv[0] << " input_file" << endl;
    return 0;
  }
}
