import multiprocessing
import numpy as np
import cv2
import time

def plot_colormap(queue):
    while True:
        data = queue.get()
        if data is None:
            break
        
        # Reshape the 1D array into a 2D array (4x8)
        data_matrix = np.reshape(data, (8, 4))

        # Scale the values to 0-255 for better visualization
        val_range = np.max(data_matrix) - np.min(data_matrix)
        data_matrix = (data_matrix / val_range * 255).astype(np.uint8)

        # Create a colormap image using OpenCV
        colormap = cv2.applyColorMap(data_matrix, cv2.COLORMAP_BONE)

        scaled_colormap = cv2.resize(colormap, (400, 800), interpolation=cv2.INTER_NEAREST)  # Adjust the size as needed

        # Display the resized colormap image
        cv2.imshow('Colormap', scaled_colormap)
        cv2.waitKey(1)

if __name__ == '__main__':
    # Create a multiprocessing queue
    queue = multiprocessing.Queue()

    # Start the process
    process = multiprocessing.Process(target=plot_colormap, args=(queue,))
    process.start()

    # Simulate continuous data sending (Replace this with your actual data source)
    while True:
        # Generate random data for demonstration
        data = np.random.rand(32)

        # Put the data into the queue
        queue.put(data)

        # Simulate the 40Hz frequency
        time.sleep(1/40)

    # End the process
    queue.put(None)
    process.join()
