from collections import deque

data_source = "ABCDEF"

class QueueFlow:
    data = data_source

    def __init__(self):
        self.queue = deque()
        self.buffer = {}
        self.END = False

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

    def end(self, message):
        self.END = True 
        print(f"Flow is done! Message: {message}")

    # The next method encapsulates the lambda creation
    def next(self, step_function, *args):
        self.queue.append(lambda: step_function(*args))

    def run(self):
        # Start the flow
        self.next(self.start)

        # Process the queue
        while self.queue:
            next_step = self.queue.popleft()
            next_step()

if __name__ == "__main__":
    
    
    data_source = "HELLO WORLD"
    flow = QueueFlow()
    flow.run()

    print(flow.END)
