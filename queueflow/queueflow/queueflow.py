from collections import deque
from functools import wraps
import signal


class TimeoutException(Exception):
    pass

def time_limit(seconds):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutException(f"Function timed out after {seconds} seconds")

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Set the signal handler and alarm
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                # Disable the alarm after the function execution
                signal.alarm(0)
            return result
        return wrapper
    return decorator


def multiple_input_step(num_input=2):
    """Decorator to collect 'input' number of data points before proceeding"""
    
    def decorator(func):
        @wraps(func)
        def wrapper(self, data, *args, **kwargs):
            # Use the function's name as the buffer key
            func_name = func.__name__
            
            # Initialize the buffer if it does not exist for this function name
            if func_name not in self.buffer:
                self.buffer[func_name] = []

            # Append the new data to the buffer
            self.buffer[func_name].append(data)
            
            # If we don't have enough inputs yet, return and wait
            if len(self.buffer[func_name]) < num_input:
                return f"Waiting for {num_input - len(self.buffer[func_name])} more inputs..."
            
            # Otherwise, we have enough inputs, call the original method
            result = func(self, self.buffer[func_name], *args, **kwargs)
            
            # Reset the buffer after processing
            self.buffer[func_name] = []
            
            return result
        return wrapper
    return decorator



class QueueFlow:
    
    def __init__(self,datax=""):
        self.data = datax
        self.queue = deque()
        self.buffer = {}
        self.END = False
        self.output = {}

    def start(self):
        print(self.data)
        result = self.data
        # Use self.next to queue the next step with arguments
        self.next(self.compare, result)
        self.next(self.compare, result[::-1])


    #Waiting for more inputs to be ready
    def compare(self, data):
        if "compare" not in self.buffer:
            self.buffer["compare"] = []

        self.buffer["compare"].append(data)

        if len(self.buffer["compare"]) < 2:
            return
        else:

            # Do comparison here !

            out = "COMPARE : ", " ||| ".join(self.buffer["compare"])
            self.next(self.end, out)

    def end(self, message , success=True):
        self.END = success
        self.SUCCESS = success
        if self.END:
            self.output["result"] = message
        else:
            self.output["result"] = ""
            self.output["error_message"] = message
        #print(f"Flow is done! Message: {message}")

    # The next method encapsulates the lambda creation
    def next(self, step_function, *args):
        self.queue.append(lambda: step_function(*args))

    def run(self):
        # Start the flow
        self.next(self.start)

        # Process the queue
        while self.queue:
            next_step = self.queue.popleft()
            try:
                next_step()
            except TimeoutException as e:
                self.end("TimeOut Exception", success=False)
            except Exception as e:
                print(f"An unexpected exception occurred: {e}")
                

if __name__ == "__main__":
    
    flow = QueueFlow("HELLO WORLD")
    flow.run()

    print(flow.END)
