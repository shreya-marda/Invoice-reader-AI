from product_matching.data_preprocessing import clean_size

def search_product_by_vector(query_embedding, size, collection):
    """Search for the best matching product using vector search and size similarity."""
    pipeline = [
        {
            "$vectorSearch": {
                "index": "name1_lab1_size3_index" if size != "N/A" else "promo_vector_index",
                "path": "emb_name1_lab1_size3" if size!="N/A" else "embeddings_new",
                "queryVector": query_embedding,
                "numCandidates": 10000,
                "limit": 30
            }
        },
        {
            "$project": {
                "globalId": 1,
                "name": 1,
                "ean": 1,
                "cai": 1,
                "label": 1,
                "display_size": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        },
        {
            "$match": {
                "score": {"$gte": 0.85}
            }
        },
        {
            "$set": {
                "similarity_score": {
                    "$cond": [
                        {"$regexMatch": {"input": clean_size("$display_size"), "regex": size if size!="N/A" else ""}},
                        0.3 if size!="N/A" else 0,  # Bonus for exact size match
                        {"$cond": [
                            {"$regexMatch": {
                                "input": "$display_size",
                                "regex": size.split(" ")[0] if size else 'NOT AVAILABLE'
                            }},
                            0.1,  # Bonus for partial size match
                            -1
                        ]}
                    ]
                }
            }
        },
        {
            "$addFields": {
                "final_score": {"$add": ["$score", "$similarity_score"]}
            }
        },
        {
            "$match": {
                "final_score": {"$gte": 0.85}
            }
        },
        {
            "$sort": {
                "final_score": -1
            }
        },
        {
            "$limit": 1
        }
    ]

    return list(collection.aggregate(pipeline))
