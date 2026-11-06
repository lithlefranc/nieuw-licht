import os
import argparse
import torch
import xml.etree.ElementTree as ET
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch.nn.functional as F
import unicodedata
import re
import ftfy
import html

def fix_encoding_issues(text):
    if text:
        text = html.unescape(text)
        text = ftfy.fix_text(text)
        text = unicodedata.normalize("NFKC", text)
        text = re.sub(r'[^\x20-\x7E]', '', text)  # Keeps only printable ASCII
    return text

def decode(inputs, labels, probs):
    input_seq, label_seq, prob_seq = [], [], []
    buffer_input, buffer_label, buffer_prob = [], [], []
    
    for subtok, subl, subp in zip(inputs, labels, probs):
        if subtok in ['<s>', '</s>', '<pad>']:
            continue
        
        if subtok.startswith('Ġ') or subtok.startswith('##'):
            if buffer_input:
                input_seq.append("".join(buffer_input))
                label_seq.append(buffer_label[0])
                prob_seq.append(buffer_prob[0])
                buffer_input, buffer_label, buffer_prob = [], [], []
            subtok = subtok.lstrip('Ġ').lstrip('##')
            if subtok:
                buffer_input.append(subtok)
                buffer_label.append(subl)
                buffer_prob.append(subp)
        else:
            buffer_input.append(subtok)
            buffer_label.append(subl)
            buffer_prob.append(subp)
    
    if buffer_input:
        input_seq.append("".join(buffer_input))
        label_seq.append(buffer_label[0])
        prob_seq.append(buffer_prob[0])
    
    return input_seq, label_seq, prob_seq

def process_text(text, model, tokenizer, device):
    if not text.strip():
        return text
    
    tokens = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    tokens = {k: v.to(device) for k, v in tokens.items()}
    
    with torch.no_grad():
        outputs = model(**tokens).logits
    
    probs = F.softmax(outputs, dim=2)
    prob_values, predictions = torch.max(probs, dim=2)
    words = tokenizer.convert_ids_to_tokens(tokens['input_ids'].squeeze().tolist())
    
    decoded_words, labels, _ = decode(words, [model.config.id2label[p] for p in predictions.squeeze().tolist()], prob_values.squeeze().tolist())
    
    output_text = []
    current_entity = None
    entity_words = []
    
    for word, label in zip(decoded_words, labels):
        label_clean = label.split("-")[-1] if label != "O" else None
        
        if label_clean:
            if current_entity == label_clean:
                entity_words.append(word)
            else:
                if current_entity:
                    output_text.append(f"<{current_entity}>{' '.join(entity_words)}</{current_entity}>")
                current_entity = label_clean
                entity_words = [word]
        else:
            if current_entity:
                output_text.append(f"<{current_entity}>{' '.join(entity_words)}</{current_entity}>")
                current_entity = None
                entity_words = []
            output_text.append(word)
    
    if current_entity:
        output_text.append(f"<{current_entity}>{' '.join(entity_words)}</{current_entity}>")
    
    processed_text = " ".join(output_text)
    return fix_encoding_issues(processed_text)

def process_xml(input_path, output_path, model, tokenizer, device):
    try:
        tree = ET.parse(input_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"❌ XML Parsing Error in {input_path}: {e}")
        return
    
    for elem in root.iter():
        if elem.tag in ["p", "marg"] and elem.text:
            processed_text = process_text(elem.text, model, tokenizer, device)
            elem.text = processed_text
    
    xml_str = ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")
    xml_str = xml_str.replace("&lt;", "<").replace("&gt;", ">")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml_str)
    
    print(f"✅ Processed XML saved as: {output_path}")

def load_model(model_name, device):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForTokenClassification.from_pretrained(model_name)
    model.to(device)
    return model, tokenizer

def main():
    parser = argparse.ArgumentParser(description="Process XML files in a folder with NER models.")
    parser.add_argument("folder", type=str, help="Path to the folder containing XML files")
    parser.add_argument("fine_model", type=str, help="Path to the fine-grained NER model")
    parser.add_argument("coarse_model", type=str, help="Path to the coarse-grained NER model")
    args = parser.parse_args()
    
    folder_path = args.folder
    fine_model_path = args.fine_model
    coarse_model_path = args.coarse_model
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    print(f"🔄 Loading fine model: {fine_model_path}...")
    model_fine, tokenizer_fine = load_model(fine_model_path, device)
    
    print(f"🔄 Loading coarse model: {coarse_model_path}...")
    model_coarse, tokenizer_coarse = load_model(coarse_model_path, device)
    
    for file in os.listdir(folder_path):
        if file.endswith("_numbered.xml"):
            input_file = os.path.join(folder_path, file)
            fine_output_file = os.path.join(folder_path, file.replace("_numbered.xml", "_fine.xml"))
            coarse_output_file = os.path.join(folder_path, file.replace("_numbered.xml", "_coarse.xml"))
            
            print(f"\n🔹 Processing {file} with fine model...")
            process_xml(input_file, fine_output_file, model_fine, tokenizer_fine, device)
            
            print(f"\n🔹 Processing {file} with coarse model...")
            process_xml(input_file, coarse_output_file, model_coarse, tokenizer_coarse, device)
    
if __name__ == "__main__":
    main()
