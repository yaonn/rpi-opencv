import cv2 as cv
import sys
import numpy as np

# Display barcode and QRcode location
def display(im, bbox):
  n=len(bbox)
  for j in range(n):
    cv.line(im, tuple(bbox[j][0]), tuple(bbox[ (j+1)%n][0]), (255,0,0), 3)

  # Display results
  cv.imshow("Results", im)

def main():
  # initialize the cam
  webcam = cv.VideoCapture(0, cv.CAP_DSHOW)
  # initialize the cv2 QRCode detector
  # detector = cv.QRCodeDetector()

  # webcamS = (int(webcam.get(cv.CAP_PROP_FRAME_WIDTH)), int(webcam.get(cv.CAP_PROP_FRAME_HEIGHT)))
  WIN_WEBCAM = 'webcam'
  cv.namedWindow(WIN_WEBCAM, cv.WINDOW_AUTOSIZE)

  framenum = -1 # Frame counter
  while True: # Show the image captured in the window and repeat
    _, frameWebcam = webcam.read()

    if frameWebcam is None:
      print('<<<Game Over>>>')
      break
    
    # if qrcodeDetector.detectAndDecodeMulti(frameWebcam):
    # data, bbox, _ = detector.detectAndDecode(frameWebcam)
    # # check if there is a QRCode in the image
    # if bbox is not None:
    #   # display the image with lines
    #   display(frameWebcam, bbox)
    #   if data:
    #     print(f'[+] QRCode detected, data:{data}')
    
      # rectifiedImage = np.uint8(rectifiedImage)
      # cv.imshow('Results', rectifiedImage)
      # break

    framenum += 1

    cv.imshow(WIN_WEBCAM, frameWebcam)

    k = cv.waitKey(30)
    if k == 27:
      break

  webcam.release()
  cv.destroyAllWindows()
  sys.exit(0)

if __name__ == '__main__':
  main()