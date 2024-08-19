# Run Module

The run module is arguably the most important part of the *alma* interface. It is here where the actual experiment/task has to be implemented. For *pyalma* the run module is merely a python file implementing a specified interface so that *pyalma* can load and execute it. Let's have a look at a short but yet extensive example.

```python
import random
import os

def run(instance, save, state):
    lines = open(instance).readlines()
    
    num_line_to_extract = int(state) if state != "" else 10
    
    with open("lines.txt", "a") as data_file:
    
        while num_line_to_extract > 0:
            data_file.write(random.choice(lines))
            
            num_line_to_extract -= 1
            save(str(num_line_to_extract))
    
# optional
def done():
    os.system("systemctl suspend")
```

This example implementation extracts 10 lines of each instance and accumulates them in a file called `lines.txt`. After every line we tell *pyalma* to save the number of lines left. This happens in the `save(str(num_line_to_extract))` line, where we call the state saving callback (`save(data : string)`) provided by the framework. When `run(...)` is being called it might not be the first time. Maybe it actually got called on that instance earlier on but got interrupted before all 10 lines where extracted. Luckily we saved our `state` (number of lines left) and *pyalma* is kind enough to pass us the saved state. With some sanity checking (if we never saved any state *pyalma* will pass us an empty string) we can load the number of lines left and we are able to continue our work where got interrupted.

After everything is done, meaning `run(...)` got executed on all instances, *pyalma* will call the `done()` function **if** specified. We decided to go to lunch while our experiment runs and to save electricity we implemented a `done()` function to suspend the computer after he is done extracting random lines.

## Interface

As the name suggest the `run(...)` function is what the *pyalma* worker will run on all specified instances. It takes three parameters:

### The run(...) function

`instance : string`
: The instance parameter is the path to the instance. With this path we can load our instance and perform whatever task we need to perform on it.

`save : void(string)`
: This callback can be used to save the current state of our execution. States are saved per instance and should by convention be marshaled into a string.

`state : string`
: If a state got saved for that instance in an earlier call, this parameter will contain the marshaled (string) state. If no state exists for an instance an empty string will be passed. Note that the marshaling and unmarshaling of states is left to the user who implements the run function.

### The done() function

Implementing this function is optional but can be useful if some actions have to be executed after everything is done. If specified/implemented *pyalma* will call `done()` after `run(...)` got called on all instances and **terminated** successfully for every instance. Interrupted executions will be called again.
