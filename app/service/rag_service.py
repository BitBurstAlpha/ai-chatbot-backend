# app/services/simple_rag_service.py
import logging
import os
from flask import current_app
from app import db
from app.models.knowledge import KnowledgeBase
from openai import OpenAI

from app.service.storage_service import download_from_s3

# Set up logger
logger = logging.getLogger(__name__)

def extract_chunks_from_s3(knowledge_ids, max_chunks=5):
    """Download and extract chunks from documents in S3.
    
    Args:
        knowledge_ids (list): List of knowledge IDs to retrieve
        max_chunks (int): Maximum number of chunks to retrieve
        
    Returns:
        list: List of text chunks with source information
    """
    try:
        # Get knowledge entries
        knowledge_entries = db.session.query(KnowledgeBase).filter(
            KnowledgeBase.id.in_(knowledge_ids)
        ).all()
        
        chunks = []
        temp_dir = os.path.join(current_app.config['TEMP_FOLDER'], 'temp_downloads')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Process each knowledge entry
        for entry in knowledge_entries:
            # Skip entries without S3 key
            if not entry.s3_key:
                continue
                
            # Create local temp path
            local_path = os.path.join(temp_dir, f"temp_{entry.id}_{os.path.basename(entry.s3_key)}")
            
            # Download file from S3
            if download_from_s3(entry.s3_key, local_path):
                # Extract text from file
                with open(local_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                
                # Simple chunking by paragraphs
                paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
                
                # Add paragraphs as chunks with source info
                for i, paragraph in enumerate(paragraphs):
                    if len(paragraph) > 100:  # Only include substantial paragraphs
                        chunks.append({
                            'text': paragraph,
                            'source': entry.title,
                            'doc_id': entry.id
                        })
                
                # Clean up temp file
                os.remove(local_path)
                
                # Break if we have enough chunks
                if len(chunks) >= max_chunks:
                    break
        
        return chunks[:max_chunks]
        
    except Exception as e:
        logger.error(f"Error extracting chunks from S3: {str(e)}")
        return []

def generate_rag_response(query, knowledge_ids):
    """Generate a response using RAG with DeepSeek.
    
    Args:
        query (str): User query
        knowledge_ids (list): List of knowledge IDs to use as context
        
    Returns:
        dict: Response with answer and sources
    """
    try:
        # Extract chunks from S3
        chunks = extract_chunks_from_s3(knowledge_ids)
        
        if not chunks:
            return {
                "answer": "No relevant information found in the selected knowledge sources.",
                "sources": []
            }
        
        # Format context
        context = "\n\n".join([f"From {chunk['source']}:\n{chunk['text']}" for chunk in chunks])
        
        # Format prompt
        prompt = f"""You are a helpful assistant. Answer based on the provided context.

Context:
{context}

Question: {query}

Answer:"""

        # Get DeepSeek client
        client = OpenAI(
            api_key=current_app.config['DEEPSEEK_API_KEY'],
            base_url=current_app.config['DEEPSEEK_API_URL'].rstrip('/') + '/v1'
        )
        
        # Generate response
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Answer concisely and naturally based on the given context, without mentioning 'provided context'."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        # Return response with sources
        return {
            "answer": response.choices[0].message.content,
        }
        
    except Exception as e:
        logger.error(f"Error generating RAG response: {str(e)}")
        return {
            "error": str(e)
        }