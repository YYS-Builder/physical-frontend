from typing import List, Dict, Any, Optional
import numpy as np
from . import logger, monitor
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import re

class AIModel:
    def __init__(self, model_name: str = "default"):
        self.model_name = model_name
        self.logger = logger.logger
        self.initialized = False
        self.summarizer = None
        self.tokenizer = None
        self.model = None
        self.vectorizer = None
        self.kmeans = None
        nltk.download('punkt')
        nltk.download('stopwords')

    async def initialize(self):
        """Initialize the AI model."""
        try:
            # Initialize summarization pipeline
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            
            # Initialize sentence transformer for embeddings
            self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
            self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
            
            # Initialize text vectorizer for clustering
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words=stopwords.words('english')
            )
            self.kmeans = KMeans(n_clusters=5, random_state=42)
            
            self.initialized = True
            self.logger.info(f"AI model {self.model_name} initialized")
        except Exception as e:
            self.logger.error(f"Error initializing AI model: {str(e)}")
            monitor.track_error("AIModel", str(e))
            raise

    async def process_document(self, document_path: str) -> Dict[str, Any]:
        """Process a document and extract relevant information."""
        if not self.initialized:
            raise RuntimeError("Model not initialized")

        try:
            # Read document content
            with open(document_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Generate summary
            summary = self.summarizer(content, max_length=130, min_length=30, do_sample=False)[0]['summary_text']

            # Extract entities and key phrases
            sentences = sent_tokenize(content)
            entities = self._extract_entities(sentences)
            key_phrases = self._extract_key_phrases(sentences)

            # Generate embeddings
            embeddings = await self.generate_embeddings(content)

            # Analyze reading difficulty
            difficulty = self._analyze_reading_difficulty(content)

            result = {
                "text": content,
                "summary": summary,
                "entities": entities,
                "key_phrases": key_phrases,
                "embeddings": embeddings.tolist(),
                "metadata": {
                    "reading_difficulty": difficulty,
                    "estimated_reading_time": self._estimate_reading_time(content),
                    "word_count": len(content.split()),
                    "sentence_count": len(sentences)
                }
            }
            
            self.logger.info(f"Document processed: {document_path}")
            monitor.track_request(0)  # Track AI operation
            return result
        except Exception as e:
            self.logger.error(f"Error processing document: {str(e)}")
            monitor.track_error("AIModel", str(e))
            raise

    async def generate_embeddings(self, text: str) -> np.ndarray:
        """Generate embeddings for a given text."""
        try:
            # Tokenize text
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            
            # Generate embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1).numpy()
            
            return embeddings
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {str(e)}")
            raise

    async def analyze_reading_patterns(self, analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze reading patterns from document analytics."""
        try:
            # Extract features from analytics
            features = self._extract_features(analytics)
            
            # Cluster reading patterns
            clusters = self._cluster_patterns(features)
            
            # Generate insights
            insights = self._generate_insights(clusters, analytics)
            
            return {
                "patterns": clusters,
                "insights": insights,
                "recommendations": self._generate_recommendations(insights)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing reading patterns: {str(e)}")
            raise

    def _extract_entities(self, sentences: List[str]) -> List[str]:
        """Extract named entities from sentences."""
        # Simple entity extraction using regex patterns
        entities = []
        for sentence in sentences:
            # Extract capitalized phrases
            entities.extend(re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', sentence))
        return list(set(entities))

    def _extract_key_phrases(self, sentences: List[str]) -> List[str]:
        """Extract key phrases from sentences."""
        # Simple key phrase extraction using TF-IDF
        if not sentences:
            return []
        
        # Fit vectorizer
        X = self.vectorizer.fit_transform(sentences)
        
        # Get feature names
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Get top phrases
        top_phrases = []
        for i in range(len(sentences)):
            feature_index = X[i,:].nonzero()[1]
            tfidf_scores = zip(feature_index, [X[i, x] for x in feature_index])
            sorted_scores = sorted(tfidf_scores, key=lambda x: x[1], reverse=True)
            top_phrases.extend([feature_names[i] for i, _ in sorted_scores[:3]])
        
        return list(set(top_phrases))

    def _analyze_reading_difficulty(self, text: str) -> str:
        """Analyze the reading difficulty of a text."""
        # Simple readability analysis
        words = text.split()
        sentences = sent_tokenize(text)
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        avg_sentence_length = len(words) / len(sentences)
        
        if avg_word_length > 6 and avg_sentence_length > 20:
            return "Advanced"
        elif avg_word_length > 5 and avg_sentence_length > 15:
            return "Intermediate"
        else:
            return "Basic"

    def _estimate_reading_time(self, text: str) -> int:
        """Estimate reading time in minutes."""
        words = text.split()
        return max(1, len(words) // 200)  # Assuming 200 words per minute

    def _extract_features(self, analytics: Dict[str, Any]) -> np.ndarray:
        """Extract features from analytics data."""
        features = []
        for session in analytics.get('reading_sessions', []):
            features.append([
                session.get('duration', 0),
                session.get('pages_read', 0),
                session.get('completion_percentage', 0),
                session.get('reading_speed', 0)
            ])
        return np.array(features)

    def _cluster_patterns(self, features: np.ndarray) -> Dict[str, Any]:
        """Cluster reading patterns."""
        if len(features) == 0:
            return {"clusters": []}
        
        # Fit K-means
        self.kmeans.fit(features)
        
        # Get cluster centers
        centers = self.kmeans.cluster_centers_
        
        return {
            "clusters": centers.tolist(),
            "labels": self.kmeans.labels_.tolist()
        }

    def _generate_insights(self, clusters: Dict[str, Any], analytics: Dict[str, Any]) -> List[str]:
        """Generate insights from reading patterns."""
        insights = []
        
        # Analyze reading speed
        avg_speed = np.mean([s.get('reading_speed', 0) for s in analytics.get('reading_sessions', [])])
        if avg_speed > 300:
            insights.append("You read faster than average")
        elif avg_speed < 150:
            insights.append("You read slower than average")
        
        # Analyze completion rate
        completion_rates = [s.get('completion_percentage', 0) for s in analytics.get('reading_sessions', [])]
        if np.mean(completion_rates) > 80:
            insights.append("You have a high completion rate")
        elif np.mean(completion_rates) < 30:
            insights.append("You tend to leave documents unfinished")
        
        return insights

    def _generate_recommendations(self, insights: List[str]) -> List[str]:
        """Generate recommendations based on insights."""
        recommendations = []
        
        for insight in insights:
            if "read faster than average" in insight:
                recommendations.append("Consider taking more breaks to improve comprehension")
            elif "read slower than average" in insight:
                recommendations.append("Try using a reading guide to improve speed")
            elif "high completion rate" in insight:
                recommendations.append("Great job! Consider exploring more challenging content")
            elif "leave documents unfinished" in insight:
                recommendations.append("Try setting smaller reading goals to improve completion rate")
        
        return recommendations

# Create global model instance
model = AIModel() 