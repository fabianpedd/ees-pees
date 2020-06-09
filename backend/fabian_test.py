import time
import automate
import subprocess

from james import RndWebotAgent

print("start webot")
w = automate.WebotCtrl()
w.init()

# print("start external")
# e = automate.ExtCtrl()
# e.init()

print("start environment")
w.start_env()

print("print data")
w.print()

print("random actions")
timmy = RndWebotAgent()
for _ in range(10):
    timmy.action()

print("wating for reset")
time.sleep(3.0)

w.reset_environment()


time.sleep(2.0)
print("random actions")
timmy = RndWebotAgent()
for _ in range(20):
    timmy.action()

time.sleep(500.0)

print("kill")
w.close()
# e.close()
