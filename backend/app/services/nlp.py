from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

class PatentAnalyzer:
    def __init__(self):
        self.summarizer = LsaSummarizer()
        self.tokenizer = Tokenizer("english")
        
    def summarize(self, text: str, sentences_count=1):
        """Improved extractive summarization"""
        try:
            parser = PlaintextParser.from_string(text, self.tokenizer)
            summary = self.summarizer(parser.document, sentences_count)
            return {
                "summary": " ".join(str(s) for s in summary),
                "method": "LSA (Algorithmic)"
            }
        except Exception as e:
            return {"error": str(e)}
            