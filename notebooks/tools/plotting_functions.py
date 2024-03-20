import matplotlib.pyplot as plt

def plot_single_meas_component(data, component):
  
  plt.plot(data[component], label=component)
  plt.xlabel('Time')
  plt.ylabel(f'{component} [uT]')
  
  plt.show()
  
def plot_meas_axis(data, letter, array_size):
  
  fig, axs = plt.subplots(array_size, 1, figsize=(12, 8))
  
  for i in range(array_size):
    axs[i].plot(data[f'{letter}{i}'], label=f'{letter}{i}')
    
  plt.xlabel('Time')
  plt.ylabel(f'{letter} [uT]')
  plt.legend()
  
  plt.show()