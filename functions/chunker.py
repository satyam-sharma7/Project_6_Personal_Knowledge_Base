def recursive_split(text, chunk_size=250, chunk_overlap=70, separators=["\n\n", "\n", " ", ""]):
    # Base case: if it fits, we are done
    if len(text) <= chunk_size:
        return [text]
    
    # Find the first separator that actually splits the text
    for sep in separators:
        if sep == "" or sep in text:
            parts = text.split(sep) if sep != "" else list(text)
            
            chunks = []
            current_chunk = ""
            
            for part in parts:
                item = part + sep if sep != "" else part
                
                # If adding this piece exceeds size, save current and roll over the overlap
                if len(current_chunk) + len(item) > chunk_size:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    
                    # Core Overlap Logic: 
                    # Grab the last 'chunk_overlap' characters from the finished chunk
                    overlap_str = current_chunk[-chunk_overlap:] if chunk_overlap > 0 else ""
                    current_chunk = overlap_str + item
                else:
                    current_chunk += item
            
            if current_chunk:
                chunks.append(current_chunk.strip())
                
            # Recursively handle any individual chunk that is STILL too big
            final_chunks = []
            for chunk in chunks:
                if len(chunk) > chunk_size:
                    next_seps = separators[separators.index(sep) + 1:]
                    # Pass chunk_overlap down through the recursion
                    final_chunks.extend(recursive_split(chunk, chunk_size, chunk_overlap, next_seps))
                else:
                    final_chunks.append(chunk)
                    
            return final_chunks
        

