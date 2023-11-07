# if 'Hire' in 'Hire)':
#     print("Exists")
# else:
#     print("Does not exist")


# x = "hiehe/"

# print(x[:-1])
# import socket as s

# host = 'https://www.jobstreet.com.sg/Engineer-jobs/mechanical-engineer-jobs'
# host_array = host.split('/')
# print(host_array)
# ip = s.gethostbyname(host_array[2])


# print('The IP Address of ' + host + ' is: '  + ip)


import winsound

def make_noise():
  duration = 1000  # milliseconds
  freq = 440  # Hz
  winsound.Beep(freq, duration)

make_noise()
