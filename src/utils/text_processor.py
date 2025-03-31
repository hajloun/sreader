class TextProcessor:
    def __init__(self):
        self.text = ""
        self.words = []

    def set_text(self, text):
        """Set the text to be processed"""
        self.text = text.strip()
        # Split text into words, removing empty strings
        self.words = [word for word in self.text.split() if word]

    def get_words(self):
        """Return the list of processed words"""
        return self.words
