import cv2 as cv
import sys
import numpy as np
import pyzbar.pyzbar as pyzbar

def decode(im) : 
    # Find barcodes and QR codes
    decodedObjects = pyzbar.decode(im)
    # Print results
    # for obj in decodedObjects:
    #     print(f'Type : {obj.type}'')
    #     print(f'Data : {obj.data,}\n')     
    return decodedObjects

font = cv.FONT_HERSHEY_SIMPLEX

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
  WIN_WEBCAM = 'webcam'
  cv.namedWindow(WIN_WEBCAM, cv.WINDOW_AUTOSIZE)

  while (webcam.isOpened()): # Show the image captured in the window and repeat
    _, frameWebcam = webcam.read()

    if frameWebcam is None:
      print('<<<Game Over>>>')
      break
    im = cv.cvtColor(frameWebcam, cv.COLOR_BGR2GRAY)
    decodedObjects = decode(im)
    
    for decodedObject in decodedObjects: 
      points = decodedObject.polygon
    
      # If the points do not form a quad, find convex hull
      if len(points) > 4 : 
        hull = cv.convexHull(np.array([point for point in points], dtype=np.float32))
        hull = list(map(tuple, np.squeeze(hull)))
      else : 
        hull = points
      
      # Number of points in the convex hull
      n = len(hull)     
      # Draw the convext hull
      for j in range(0,n):
        cv.line(frameWebcam, hull[j], hull[ (j+1) % n], (255,0,0), 3)

      x = decodedObject.rect.left
      y = decodedObject.rect.top

      print(x, y)
      print(f'Type : {decodedObject.type}')
      print(f'Data : {decodedObject.data,}\n')

      barCode = str(decodedObject.data)
      cv.putText(frameWebcam, barCode, (x, y), font, 1, (0,255,255), 2, cv.LINE_AA)

    # Display the resulting frame
    cv.imshow(WIN_WEBCAM, frameWebcam)

    key = cv.waitKey(3)
    if key & 0xFF == ord('q'):
      break
    elif key & 0xFF == ord('s'): # wait for 's' key to save 
        cv.imwrite('Capture.png', frameWebcam)

  # When everything done, release the capture
  webcam.release()
  cv.destroyAllWindows()
  sys.exit(0)

if __name__ == '__main__':
  main()