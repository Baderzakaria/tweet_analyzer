import praw
from textblob import TextBlob
from langdetect import detect
from translate import Translator
import os
from dotenv import load_dotenv

load_dotenv()

# Connexion à Reddit
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

def detect_language(text):
    try:
        return detect(text)
    except Exception as e:
        print(f"Erreur lors de la détection de langue : {e}")
        return "unknown"

def translate_to_french(text, source_lang):
    try:
        if source_lang != "fr" and source_lang != "unknown":
            translator = Translator(from_lang=source_lang, to_lang="fr")
            return translator.translate(text)
        return text
    except Exception as e:
        print(f"Erreur lors de la traduction : {e}")
        return text

def analyze_sentiment(text):
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        if polarity > 0.1:
            return "positive"
        elif polarity < -0.1:
            return "negative"
        else:
            return "neutral"
    except Exception as e:
        print(f"Erreur lors de l'analyse des sentiments : {e}")
        return "unknown"

def get_reddit_comments(keyword, limit=50):
    try:
        comments = []
        for submission in reddit.subreddit("all").search(keyword, limit=limit):
            submission.comments.replace_more(limit=0)
            for comment in submission.comments.list():
                if len(comments) < limit:
                    text = comment.body.strip()
                    language = detect_language(text)
                    translation = translate_to_french(text, language)
                    sentiment = analyze_sentiment(translation)

                    comments.append({
                        "OriginalText": text,
                        "Language": language,
                        "Translation": translation,
                        "Sentiment": sentiment
                    })
                else:
                    break
        return comments
    except Exception as e:
        print(f"Erreur lors de la récupération des commentaires Reddit : {e}")
        return []

