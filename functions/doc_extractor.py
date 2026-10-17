from pypdf import PdfReader
import pathlib
    
def doc_type(path):
    if path.is_file():
        if path.suffix == ".pdf":
            file_content, file_name = pdf_exctratror(path)
            return file_content, file_name
        elif path.suffix == ".md" or path.suffix == ".txt":
            file_content, file_name = md_txt_extractor(path)
            return file_content, file_name
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}")

def pdf_exctratror(path):
    content = ""
    file_name = path.name
    file = PdfReader(path)
    for page in file.pages:
        content += page.extract_text()
        content += "\n\n"
    
    return content, file_name
    

def md_txt_extractor(path):
    file_name = path.name
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    return content, file_name
        


def extracted_content(file_path: str):
    content = {}
    path = pathlib.Path(file_path)

    if path.is_dir():
        for f in path.iterdir():
            if f.is_file():
                try:
                    file_content, file_name = doc_type(f)
                    content[file_name] = file_content
                except FileNotFoundError:
                    continue
                except ValueError:
                    continue
    
    if path.is_file():
        try:
            file_content, file_name = doc_type(path)
            content[file_name] = file_content
        except FileNotFoundError:
            print("Please provide a valid file path.")
    
    return content

