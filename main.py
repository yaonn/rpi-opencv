import cv2 as cv
import sys, requests, os
import jwt
import numpy as np
import pyzbar.pyzbar as pyzbar
from dotenv import load_dotenv
from py2neo import Graph
import json
from threading import Thread
import tkinter
load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")
root = tkinter.Tk()
displayWidth = root.winfo_screenwidth()
displayHeight = root.winfo_screenheight()
graph = Graph("bolt://olfact.io:7687", auth=("neo4j", "admin"))
print(graph.run("match (shop:Shop {slug:$slug}) return shop", slug='songyan'))
createUser2Shop = """
MATCH (shop:Shop {slug:toString($doorInput.shop)}), (user:Customer {id:toString($doorInput.id)})
CALL{
  WITH shop, user
  MATCH (shop)<-[visit:VISIT]-(user)
  WHERE NOT exists(visit.isRemoved)
  SET visit.isRemoved=true, visit.updatedAt=datetime({ timezone: 'Asia/Taipei' })
  RETURN visit ORDER BY visit.createdAt LIMIT 1
}
CALL{
  WITH shop, user
  CREATE (user)-[visit:VISIT {id:apoc.create.uuid()}]->(shop)
  SET visit.createdAt = datetime({ timezone: 'Asia/Taipei' }),
  visit.doorId = $doorInput.doorId,
  visit.doorIssAt=$doorInput.doorIssAt,
  visit.getIdAt=$doorInput.getDoorIdAt
  RETURN visit AS doorOpen
}
RETURN doorOpen.id
"""

def verify_jwt(data):
  try:
    if type(data) == bytes:
      data.decode('utf-8')
    decoded = jwt.decode(data, JWT_SECRET, algorithms=["RS256"])
    if decoded:
      print(f'found id: {decoded}')
      response = requests.get('http://192.168.0.5:5010/on')
      print(response.json())
  except Exception as err:
    print(f'verify jwt: {err}')
  

def decode(im) : 
    # Find barcodes and QR codes
    decodedObjects = pyzbar.decode(im)
    # Print results
    # for obj in decodedObjects:
    #     print(f'Type : {obj.type}'')
    #     print(f'Data : {obj.data,}\n')     
    return decodedObjects

font = cv.FONT_HERSHEY_SIMPLEX

def main():
  # initialize the cam
  webcam = cv.VideoCapture(0, cv.CAP_DSHOW)
  WIN_WEBCAM = 'webcam'
  cv.namedWindow(WIN_WEBCAM, cv.WINDOW_AUTOSIZE)
  cv.moveWindow(WIN_WEBCAM, int(displayWidth/2+1), int(displayHeight/4+1))

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

      # verify_jwt(decodedObject.data)
      barCode = str(decodedObject.data)
      dictData = json.loads(decodedObject.data.decode('utf-8'))
      if not os.path.exists('buffer.txt'):
        open('buffer.txt', 'x')
      with open('buffer.txt', 'r+') as f:
        lastInput = f.read()
        print(lastInput)
        if barCode != lastInput:
          if "id" in dictData:
            print(graph.run(createUser2Shop, doorInput={
              "id": dictData["id"],
              "shop": "songyan",
              "doorId": dictData["doorId"] if "doorId" in dictData else None,
              "doorIssAt": dictData["doorIssAt"] if "doorIssAt" in dictData else None,
              "getDoorIdAt": dictData["getDoorIdAt"] if "getDoorIdAt" in dictData else None
            }).data())

            f.write(barCode)

      response =  f'Hello, {dictData["name"]}' if type(dictData["id"]) is not None else barCode
      cv.putText(frameWebcam, response, (x, y), font, 1, (0,255,255), 2, cv.LINE_AA)


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
  # Thread(target=main).start()