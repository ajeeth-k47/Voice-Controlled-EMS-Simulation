import zipfile
import re
import sys
import os

def read_docx(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    try:
        with zipfile.ZipFile(file_path) as z:
            xml_content = z.read('word/document.xml').decode('utf-8')
            # Rudimentary XML parsing to get text. 
            # w:t tags usually contain the text in docx.
            # This regex looks for <w:t>...</w:t> or <w:t ...>...</w:t>
            
             # Remove XML tags but keep some structure?
             # Simple regex to strip tags might just merge everything.
             # Attempting to find <w:p> for paragraphs to add newlines
            
            # Replace paragraph ends with newlines
            xml_content = re.sub(r'</w:p>', '\n', xml_content)
            
            # Remove all other tags
            text = re.sub(r'<[^>]+>', '', xml_content)
            
            # print(text) -- this was failing
            try:
                sys.stdout.reconfigure(encoding='utf-8')
            except:
                pass # Python < 3.7 might fail, but 3.12 is fine
            
            print(text)
    except Exception as e:
        print(f"Error reading docx: {e}")

if __name__ == "__main__":
    read_docx('Thesis_Proposal.docx')
