from click import DateTime


class queueCLI:
    def __init__(self):
        self.queue = list()
        print("Queue Cli initialized")
        pass

    def makeQueue(self, name):
        self.queueName = name
        # redis main queue ka name ki ek list ya sorted list bnalo
    def add(self, id, command, maxReteries=3):
        self.id = id
        self.command = command
        self.attempts = 0
        self.maxReteries = maxReteries
        self.createdAt = DateTime()
        self.queue.append({self.id, self.command, self.attempts, self.maxReteries, self.createdAt})
    
    def isEmpty(self):
        return self.queue.__len__==0


if(__name__=='main'):
    q = queueCLI()
    print("queue cli")
