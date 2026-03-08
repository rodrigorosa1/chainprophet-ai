import numpy as np


class SentimentService:
    def __init__(self):
        self.analyzer_kind, self.analyzer = self._get_sentiment_analyzer()

    def _get_sentiment_analyzer(self):
        try:
            from transformers import pipeline

            clf = pipeline("text-classification", model="ProsusAI/finbert", top_k=None)
            return ("finbert", clf)
        except Exception:
            try:
                from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

                return ("vader", SentimentIntensityAnalyzer())
            except Exception:
                return (None, None)

    def score(self, texts: list[str]) -> float:
        if not texts:
            return 0.0

        texts = [t for t in texts if isinstance(t, str) and t.strip()][:30]

        if self.analyzer_kind == "finbert":
            scores = []
            for text in texts:
                out = self.analyzer(text)
                best = max(out, key=lambda x: x["score"])
                label = best["label"].lower()
                score = best["score"]

                if "positive" in label:
                    scores.append(float(score))
                elif "negative" in label:
                    scores.append(float(-score))
                else:
                    scores.append(0.0)

            return float(np.mean(scores)) if scores else 0.0

        if self.analyzer_kind == "vader":
            scores = [
                float(self.analyzer.polarity_scores(text)["compound"]) for text in texts
            ]
            return float(np.mean(scores)) if scores else 0.0

        return 0.0
