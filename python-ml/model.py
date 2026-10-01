"""
model.py
--------
Text classification model for the Fake News Detector ML service.

Approach:
  A scikit-learn Pipeline combining:
    1. TF-IDF vectorization of the (cleaned) article text.
    2. Hand-engineered "sensationalism" signal features (exclamation mark
       count, ALL-CAPS word count, and a count of common clickbait /
       conspiracy trigger phrases), which are strong, cheap signals real
       fake-news classifiers use alongside pure word statistics.
  The two feature sets are combined via FeatureUnion and fed into a
  Logistic Regression classifier.

  On first run, the model trains on a bundled labeled dataset (REAL vs
  FAKE style text) and persists itself to disk with joblib. On later runs
  the cached model is loaded directly, avoiding retraining on every
  server start.

  This is intentionally lightweight (no external dataset download, no GPU
  requirement) so the service can be installed and run anywhere with just
  `pip install -r requirements.txt`. It is a demonstration/teaching model,
  not a substitute for professional fact-checking - in a real production
  system you would swap `build_training_data()` for a large labeled corpus
  (e.g. LIAR, FakeNewsNet, Kaggle Fake-and-Real-News) or replace the
  pipeline with a fine-tuned transformer (e.g. distilbert-base-uncased)
  loaded via HuggingFace `transformers`.
"""

import os
import re
import numpy as np
import joblib
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, FeatureUnion

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fake_news_model.joblib")

# ---------------------------------------------------------------------------
# Bundled mock training data.
# REAL = sober, attributed, measured reporting style.
# FAKE = sensational, unverified, conspiratorial, clickbait style.
# ---------------------------------------------------------------------------

REAL_SAMPLES = [
    "The Federal Reserve raised interest rates by a quarter point on Wednesday, citing persistent inflation pressures.",
    "Local officials confirmed that road repairs on Main Street will begin next month and are expected to last six weeks.",
    "According to a peer-reviewed study published in Nature, researchers found a modest correlation between sleep and memory retention.",
    "The city council voted 6-3 on Tuesday to approve the proposed budget for the upcoming fiscal year.",
    "Government data released this week shows unemployment fell slightly to 3.9 percent in the third quarter.",
    "The company reported quarterly earnings that matched analyst expectations, with revenue up 4 percent year over year.",
    "Health officials recommend that adults over 65 receive an annual flu vaccination before the winter season.",
    "A spokesperson for the transportation department said the new bus routes will launch on the first of next month.",
    "The university announced a new scholarship program aimed at supporting first-generation college students.",
    "Meteorologists forecast a cold front moving through the region this weekend, bringing lower temperatures and light rain.",
    "The senate committee held a hearing on Thursday to review proposed changes to the infrastructure bill.",
    "Scientists at the research institute published findings suggesting a gradual decline in local bee populations over the last decade.",
    "The mayor's office released a statement clarifying the timeline for the downtown revitalization project.",
    "Officials from the health department confirmed three new cases in the county, in line with seasonal trends.",
    "The central bank's quarterly report noted steady growth in the manufacturing sector compared to the previous year.",
    "A new bridge inspection report found the structure to be safe, with minor maintenance recommended within two years.",
    "The school board approved a revised calendar for the next academic year following public comment sessions.",
    "Researchers presented their findings at the annual conference, noting the study's sample size as a limitation.",
    "The airline announced it will resume direct flights between the two cities starting next spring.",
    "Court documents show the case has been scheduled for a preliminary hearing next month.",
    "The nonprofit organization released its annual report detailing how donations were allocated across programs.",
    "Local farmers reported a slightly above-average harvest this season due to favorable rainfall.",
    "The company's chief executive addressed shareholders during the annual meeting, outlining plans for expansion.",
    "Public health officials urged residents to stay hydrated during the ongoing heat advisory.",
    "The state legislature passed a bill requiring additional funding for rural broadband access.",
    "The World Health Organization published updated guidance on seasonal vaccination based on data from member states.",
    "Officials at the United Nations discussed proposed climate financing mechanisms during a scheduled committee session.",
    "A study conducted over five years found no significant link between the two variables researchers examined.",
    "The regulatory agency proposed new emissions standards for vehicles, subject to a 90-day public comment period.",
    "City engineers confirmed that water quality tests returned results within normal safety thresholds this quarter.",
    "The technology company issued a software update addressing a minor security vulnerability found by researchers.",
    "Analysts noted that the retailer's holiday sales figures were roughly in line with industry-wide trends.",
    "The board of education discussed staffing shortages during Monday's public meeting.",
    "A federal judge dismissed the lawsuit, ruling that the plaintiffs lacked sufficient standing.",
    "The observatory reported a minor increase in local seismic activity, consistent with historical patterns.",
    "Officials said the bridge closure is temporary and scheduled to reopen by the end of the month.",
    "The pharmaceutical company published phase two trial results in a peer-reviewed medical journal.",
    "Weather service data indicates rainfall this month was slightly above the regional seasonal average.",
    "The committee's report recommended incremental changes to the existing zoning ordinance.",
    "Union representatives and management resumed contract negotiations after a scheduled recess.",
    "The census bureau released updated population estimates for counties across the state.",
]

FAKE_SAMPLES = [
    "SHOCKING: Doctors HATE this one weird trick that cures everything overnight, government tries to ban it!",
    "You won't believe what scientists don't want you to know about this secret cure hidden for decades.",
    "BREAKING: Aliens confirmed to be living among us, secret government files leaked online!",
    "This miracle pill melts fat while you sleep, and Big Pharma is furious about it.",
    "Celebrity found dead in mysterious circumstances, insiders claim it was a cover-up all along.",
    "Vaccines contain secret microchips designed to track your every move, whistleblower reveals shocking truth.",
    "Click here now to see the forbidden footage the mainstream media refuses to show you.",
    "Experts are terrified of this ancient remedy that instantly reverses aging, banned in five countries.",
    "The moon landing was completely staged in a Hollywood studio, new evidence proves conspiracy.",
    "Government secretly poisoning the water supply to control the population, leaked memo exposes plan.",
    "This one trick will make you rich overnight, banks don't want you to know about it.",
    "Shocking video reveals politician's secret crime ring, mainstream media too scared to report it.",
    "Scientists discover cure for cancer but pharmaceutical companies bury it to protect profits.",
    "You are being watched right now through your phone camera, insiders confirm secret surveillance program.",
    "This common household item is secretly killing you and nobody is talking about it.",
    "Breaking: World leaders caught in massive scandal, mainstream media completely silent on the story.",
    "Eat this every morning to lose 20 pounds in a week, doctors are begging people to stop.",
    "Secret society controls world governments, leaked documents finally expose the shocking truth.",
    "This app is stealing your data and selling it to foreign governments, delete it immediately.",
    "Unbelievable: Man discovers free energy device, big oil companies pay him to stay silent.",
    "Anonymous insider leaks proof that the election results were secretly manipulated overnight.",
    "This forbidden fruit cures diabetes instantly but the sugar industry doesn't want you to know.",
    "Shocking new report claims the earth is actually flat and NASA has been lying for years.",
    "Miracle water heals all diseases according to secret ancient text hidden from the public.",
    "Government insiders admit weather is being controlled to manipulate the stock market, sources say.",
    "URGENT: United Nations announces emergency global ban on all smartphones starting next month.",
    "In a secret midnight emergency meeting, world leaders reportedly agreed to a total internet shutdown.",
    "An anonymous insider claims a classified, unreleased report proves the vaccine alters human DNA permanently.",
    "BREAKING: Government preparing to seize all privately owned gold within thirty days, leaked memo warns.",
    "Sources say a secret international treaty will outlaw cash entirely by the end of this year.",
    "An unreleased classified study allegedly proves that cell towers are silently erasing human memories.",
    "Whistleblower reveals secret plan to microchip every citizen under the guise of a new health initiative.",
    "URGENT WARNING: Experts claim your smart TV is secretly recording every conversation in your home.",
    "A leaked internal memo allegedly proves airlines are hiding the true danger of jet fuel exposure.",
    "Anonymous sources inside the agency claim the entire food supply is being secretly altered overnight.",
    "BREAKING: Secret emergency decree bans all social media platforms worldwide starting at midnight.",
    "An unnamed insider claims a hidden government report proves 5G towers cause instant memory loss.",
    "Shocking leaked documents reveal a secret plan to replace all currency with a hidden tracking system.",
    "URGENT: Classified sources claim world governments are hiding proof that time itself is slowing down.",
    "A so-called chief analyst warns of an imminent secret ban nobody in the mainstream media will report.",
    "Anonymous insider warns citizens to stock up immediately before a secretly planned nationwide blackout.",
    "In a stunning new study, researchers claim eating a rare fruit reverses aging instantly, but skincare companies hid the truth for decades.",
    "Lead researcher claims a simple household spice cures all diseases overnight in an exclusive interview, but big companies buried the discovery.",
    "A new report claims a common vitamin completely reverses hair loss within 48 hours, according to an exclusive interview with the study's author.",
    "Doctors are stunned after a new study finds a single food eliminates all signs of aging in two days, insiders say companies hid this for years.",
    "An exclusive interview reveals a miracle ingredient that erases wrinkles overnight, industry insiders reportedly kept it secret to protect profits.",
    "A newly released study claims a popular drink completely stops the aging process, researchers say the discovery has been suppressed for decades.",
    "A stunning new study claims eating a common vegetable daily completely reverses diabetes, but the sugar industry has hidden the truth for years.",
    "Researchers claim a single daily pill entirely eliminates the need for sleep, according to an exclusive interview the mainstream media ignored.",
    "A groundbreaking study allegedly proves a household oil cures baldness overnight, but companies have suppressed the discovery to protect profits.",
    "An exclusive new report claims scientists have created a pill that makes aging stop entirely, though skeptics say the study was never peer reviewed.",
]


def clean_text(text: str) -> str:
    """Lowercase, strip URLs and non-alphanumeric characters, collapse whitespace.
    Used only for the TF-IDF branch - the raw text is preserved separately
    for the sensationalism feature branch (which cares about case/punctuation).
    """
    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ---------------------------------------------------------------------------
# Hand-engineered "sensationalism" signal features.
# These are cheap, interpretable signals commonly used alongside bag-of-words
# features in real fake-news detectors, and they generalize much better than
# TF-IDF alone to headline styles the training set hasn't seen verbatim.
# ---------------------------------------------------------------------------

SENSATIONAL_PHRASES = [
    "urgent", "breaking", "shocking", "secret", "anonymous insider", "anonymous source",
    "classified", "unreleased", "conspiracy", "cover-up", "cover up", "banned",
    "miracle", "insider", "leaked", "exposed", "hidden truth", "won't believe",
    "you won't believe", "big pharma", "mainstream media", "whistleblower",
    "they don't want you to know", "doesn't want you to know", "stock up immediately",
    "emergency meeting", "midnight meeting", "global ban", "worldwide ban",
    "stunning new study", "exclusive interview", "hid the truth", "hidden the truth",
    "protect profits", "protect their profits", "suppressed", "peer reviewed",
    "completely reverses", "completely stops", "reverses aging", "cures all",
    "groundbreaking study",
]


class SensationalismFeatures(BaseEstimator, TransformerMixin):
    """Extracts numeric stylistic features from raw (uncleaned) text:
    exclamation mark count, ALL-CAPS word count, and sensational phrase hits.
    """

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        feats = []
        for raw_text in X:
            lower = raw_text.lower()
            exclaim_count = raw_text.count("!")
            caps_words = len(re.findall(r"\b[A-Z]{3,}\b", raw_text))
            phrase_hits = sum(1 for phrase in SENSATIONAL_PHRASES if phrase in lower)
            word_count = max(len(raw_text.split()), 1)
            # Normalize exclaim/caps by length so long articles aren't unfairly penalized.
            feats.append([
                exclaim_count,
                caps_words,
                phrase_hits,
                exclaim_count / word_count,
                caps_words / word_count,
            ])
        return np.array(feats, dtype=float)


def build_training_data():
    texts = REAL_SAMPLES + FAKE_SAMPLES
    # 0 = REAL, 1 = FAKE
    labels = [0] * len(REAL_SAMPLES) + [1] * len(FAKE_SAMPLES)
    return texts, labels


def train_model() -> Pipeline:
    texts, labels = build_training_data()

    # Raw text is passed into the pipeline; the TF-IDF branch cleans it
    # internally via its own `preprocessor`, while the sensationalism
    # branch reads the raw text directly (it needs case and punctuation).
    features = FeatureUnion([
        (
            "tfidf",
            TfidfVectorizer(
                preprocessor=clean_text,
                ngram_range=(1, 2),
                max_features=5000,
                stop_words="english",
                sublinear_tf=True,
            ),
        ),
        ("sensationalism", SensationalismFeatures()),
    ])

    pipeline = Pipeline([
        ("features", features),
        ("clf", LogisticRegression(max_iter=2000, C=2.0, class_weight="balanced")),
    ])
    pipeline.fit(texts, labels)
    joblib.dump(pipeline, MODEL_PATH)
    return pipeline


def load_model() -> Pipeline:
    if os.path.exists(MODEL_PATH):
        try:
            loaded = joblib.load(MODEL_PATH)
            # Basic sanity check: make sure the cached pipeline still has the
            # expected feature branches (guards against loading a stale
            # cache from the previous, simpler version of this model).
            if hasattr(loaded, "named_steps") and "features" in loaded.named_steps:
                return loaded
            return train_model()
        except Exception:
            return train_model()
    return train_model()


# Model is loaded (or trained once) at import time.
_model = load_model()

LABEL_MAP = {0: "REAL", 1: "FAKE"}


def predict(text: str) -> dict:
    """
    Run inference on a single piece of text.

    Returns:
        {
          "label": "REAL" | "FAKE",
          "confidence": float (0-100, confidence in the predicted label),
          "probabilities": {"REAL": float, "FAKE": float}
        }
    """
    if not text or not text.strip():
        raise ValueError("Text input is empty")

    stripped = text.strip()

    proba = _model.predict_proba([stripped])[0]
    pred_idx = int(np.argmax(proba))
    label = LABEL_MAP[pred_idx]
    confidence = round(float(proba[pred_idx]) * 100, 2)

    return {
        "label": label,
        "confidence": confidence,
        "probabilities": {
            "REAL": round(float(proba[0]) * 100, 2),
            "FAKE": round(float(proba[1]) * 100, 2),
        },
    }


def reload_model() -> Pipeline:
    """Force retraining and overwrite the persisted model artifact."""
    global _model
    _model = train_model()
    return _model