import tiktoken

def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def truncate_text(text: str, max_tokens: int = 3000) -> str:
    tokens = tiktoken.get_encoding("cl100k_base").encode(text)
    if len(tokens) <= max_tokens:
        return text
    return tiktoken.get_encoding("cl100k_base").decode(tokens[:max_tokens])