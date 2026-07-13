import re

class DataProcessor:
    """Handles parsing, cleaning, and preprocessing of raw unstructured text data."""
    
    def __init__(self):
        pass

    def clean_text(self, text: str) -> str:
        """Removes noise, special characters, extra whitespace, and standardizes casing."""
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        text = re.sub(r'\S+@\S+', '', text)
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_keywords(self, text: str, keywords_list: list) -> list:
        """Checks for the presence of specific hard skills or tools within the text."""
        cleaned_text = self.clean_text(text)
        found_keywords = [kw for kw in keywords_list if kw.lower() in cleaned_text]
        return found_keywords

if __name__ == "__main__":
    processor = DataProcessor()
    sample_resume = "Expert Python developer looking for ML roles. Contact: test@email.com"
    print("Cleaned text output:", processor.clean_text(sample_resume))