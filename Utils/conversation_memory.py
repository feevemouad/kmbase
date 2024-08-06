class ConversationMemory:
    def __init__(self, max_turns=10):
        self.history = [{"role": "assistant", "content": "How may I assist you today?"}]
        self.max_turns = max_turns

    def add_exchange(self, message):
        self.history.append(message)

    def get_context(self):
        if len(self.history) > 5:
            return self.history[-8:-1]
        else:
            return self.history[:-1]
        
    def clear(self):
        self.history = [{"role": "assistant", "content": "How may I assist you today?"}]