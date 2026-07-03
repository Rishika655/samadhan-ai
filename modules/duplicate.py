from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3

def check_duplicate(new_complaint, threshold=0.6):
    conn = sqlite3.connect('database/complaints.db')
    c = conn.cursor()
    c.execute("SELECT id, complaint FROM complaints")
    existing = c.fetchall()
    conn.close()

    if not existing:
        return None

    existing_ids = [row[0] for row in existing]
    existing_texts = [row[1] for row in existing]

    all_texts = existing_texts + [new_complaint]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    new_vector = tfidf_matrix[-1]
    existing_vectors = tfidf_matrix[:-1]

    similarities = cosine_similarity(new_vector, existing_vectors)[0]

    max_index = similarities.argmax()
    max_score = similarities[max_index]

    if max_score >= threshold:
        return {
            "is_duplicate": True,
            "duplicate_of_id": existing_ids[max_index],
            "similarity_score": round(float(max_score) * 100, 2),
            "matched_complaint": existing_texts[max_index]
        }
    
    return {"is_duplicate": False}