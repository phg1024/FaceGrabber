#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"

#include <iostream>

using namespace cv;
using namespace std;

static void help()
{
    cout << "\nThis program demonstrated the floodFill() function\n"
            "Call:\n"
            "./ffilldemo [image_name -- Default: fruits.jpg]\n" << endl;

    cout << "Hot keys: \n"
            "\tESC - quit the program\n"
            "\tc - switch color/grayscale mode\n"
            "\tm - switch mask mode\n"
            "\tr - restore the original image\n"
            "\ts - use null-range floodfill\n"
            "\tf - use gradient floodfill with fixed(absolute) range\n"
            "\tg - use gradient floodfill with floating(relative) range\n"
            "\t4 - use 4-connectivity mode\n"
            "\t8 - use 8-connectivity mode\n" << endl;
}

Mat image0, image, gray, mask;
int ffillMode = 1;
int loDiff = 20, upDiff = 20;
int connectivity = 4;
int isColor = true;
bool useMask = false;
int newMaskVal = 255;

static void onMouse( int event, int x, int y, int, void* )
{
    if( event != CV_EVENT_LBUTTONDOWN )
        return;

    Point seed = Point(x,y);
    int lo = ffillMode == 0 ? 0 : loDiff;
    int up = ffillMode == 0 ? 0 : upDiff;
    int flags = connectivity + (newMaskVal << 8) +
                (ffillMode == 1 ? CV_FLOODFILL_FIXED_RANGE : 0);
    int b = (unsigned)theRNG() & 255;
    int g = (unsigned)theRNG() & 255;
    int r = (unsigned)theRNG() & 255;
    Rect ccomp;

    Scalar newVal = isColor ? Scalar(b, g, r) : Scalar(r*0.299 + g*0.587 + b*0.114);
    Mat dst = isColor ? image : gray;
    int area;

    if( useMask )
    {
        threshold(mask, mask, 1, 128, CV_THRESH_BINARY);
        area = floodFill(dst, mask, seed, newVal, &ccomp, Scalar(lo, lo, lo),
                  Scalar(up, up, up), flags);
        imshow( "mask", mask );
    }
    else
    {
        area = floodFill(dst, seed, newVal, &ccomp, Scalar(lo, lo, lo),
                  Scalar(up, up, up), flags);
    }

    imshow("image", dst);
    cout << area << " pixels were repainted\n";
}


int main( int argc, char** argv )
{
    char* filename = argc >= 2 ? argv[1] : (char*)"fruits.jpg";
    image0 = imread(filename, 1);

    if( image0.empty() )
    {
        cout << "Image empty. Usage: ffilldemo <image_name>\n";
        return 0;
    }
    help();
    image0.copyTo(image);
    cvtColor(image0, gray, COLOR_BGR2GRAY);
    mask.create(image0.rows+2, image0.cols+2, CV_8UC1);

    namedWindow( "image", 0 );
    namedWindow( "paint", 0 );

    //setMouseCallback( "image", onMouse, 0 );

    imshow("image", image);
    imshow("paint", image);

    waitKey(0);
    return 0;
}
