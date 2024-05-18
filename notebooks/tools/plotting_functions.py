import matplotlib.pyplot as plt

def plot_single_meas_component(data, component):
  
  plt.plot(data[component], label=component)
  plt.xlabel('Time')
  plt.ylabel(f'{component} [uT]')
  
  plt.show()

def plot_taxel(data, taxel_id):
  
  fig, axs = plt.subplots(3, 1, figsize=(12, 8))
  
  for i, letter in enumerate(['X', 'Y', 'Z']):
    axs[i].plot(data[f'{letter}{taxel_id}'], label=f'{taxel_id}{i}')
    
  plt.show()

def plot_three_components(comps):
  
  X, Y, Z = comps
  
  fig, axs = plt.subplots(3, 1, figsize=(12, 8))
  
  axs[0].plot(X)  
  axs[1].plot(Y)  
  axs[2].plot(Z)    
  
  plt.show()

def plot_xy(data, show=True):
  
  plt.plot(data['X'], data['Y'])
  plt.xlabel('X [m]')
  plt.ylabel('Y [m]')
  
  plt.gca().set_aspect('equal', adjustable='box')
  plt.grid()
  
  if show:
    plt.show()
  
def plot_meas_axis(data, letter, array_size):
  
  fig, axs = plt.subplots(array_size, 1, figsize=(12, 8))
  
  for i in range(array_size):
    axs[i].plot(data[f'{letter}{i}'], label=f'{letter}{i}')
    
  plt.xlabel('Time')
  plt.ylabel(f'{letter} [uT]')
  plt.legend()
  
  plt.show()