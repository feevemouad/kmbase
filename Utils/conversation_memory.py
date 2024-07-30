class ConversationMemory:
    def __init__(self, max_turns=5):
        self.history = []
        self.max_turns = max_turns

    def add_exchange(self, user_input, model_response):
        self.history.append((user_input, model_response))
        if len(self.history) > self.max_turns:
            self.history.pop(0)

    def get_context(self):
        return "\n".join([f"user: {u}\nassistant: {a}" for u, a in self.history])

    def clear(self):
        self.history = []