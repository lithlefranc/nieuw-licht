import os
import pandas as pd
from lxml import etree
import argparse

def df2xml(df_entities, output_xml):
    df_entities["page"] = pd.to_numeric(df_entities["page"], errors="coerce")
    df_entities["incident"] = pd.to_numeric(df_entities["incident"], errors="coerce")
    df_entities["structural_element_number"] = pd.to_numeric(df_entities["structural_element_number"], errors="coerce")
    df_entities = df_entities.sort_values(by=["page", "incident", "structural_element_number"], ascending=True)

    root = "<incidents>"
    pages = df_entities.groupby("page")

    for page_num, page_group in pages:
        root += f'<page number="{int(page_num)}">'
        incidents = page_group.groupby("incident")
        for incident_num, incident_group in incidents:
            root += f'<incident number="{int(incident_num)}">'
            struct_elements = incident_group.groupby(["paragraph_type", "structural_element_number"])
            for (para_type, struct_num), struct_group in struct_elements:
                root += f'<{para_type} number="{struct_num}">' 
                open_coarse_tags = []
                open_fine_tags = []
                deferred_coarse_closings = []
                text_content = ""
                
                for _, row in struct_group.iterrows():
                    coarse = row['coarse_entity']
                    fine = row['fine_entity']
                    char = row['character']
                    
                    if isinstance(coarse, str) and coarse.startswith("B-"):
                        coarse_clean = coarse.replace('B-', '')
                        if open_fine_tags:
                            text_content += f'</{open_fine_tags.pop()}>'
                        text_content += f'<{coarse_clean}>'
                        open_coarse_tags.append(coarse_clean)
                    
                    if isinstance(fine, str) and fine.startswith("B-"):
                        fine_clean = fine.replace('B-', '')
                        if open_fine_tags:
                            text_content += f'</{open_fine_tags.pop()}>'
                        text_content += f'<{fine_clean}>'
                        open_fine_tags.append(fine_clean)
                    
                    text_content += char
                    
                    if isinstance(fine, str) and fine.startswith("F-"):
                        fine_clean = fine.replace('F-', '')
                        if fine_clean in open_fine_tags:
                            text_content += f'</{fine_clean}>'
                            open_fine_tags.remove(fine_clean)
                    
                    while deferred_coarse_closings:
                        tag_to_close = deferred_coarse_closings.pop()
                        text_content += f'</{tag_to_close}>'
                        if tag_to_close in open_coarse_tags:
                            open_coarse_tags.remove(tag_to_close)
                    
                    if isinstance(coarse, str) and coarse.startswith("F-"):
                        coarse_clean = coarse.replace('F-', '')
                        if coarse_clean in open_coarse_tags:
                            text_content += f'</{coarse_clean}>'
                            open_coarse_tags.remove(coarse_clean)
                
                while open_fine_tags:
                    text_content += f'</{open_fine_tags.pop()}>'
                while open_coarse_tags:
                    text_content += f'</{open_coarse_tags.pop()}>'
                while deferred_coarse_closings:
                    text_content += f'</{deferred_coarse_closings.pop()}>'
                
                root += text_content + f'</{para_type}>'
            root += f'</incident>'
        root += f'</page>'
    root += "</incidents>"
    
    parser = etree.XMLParser(recover=True)
    try:
        node = etree.fromstring(root.encode('utf-8'), parser)
        with open(output_xml, "wb") as f:
            f.write(etree.tostring(node, pretty_print=True, encoding="utf-8"))
        print(f"✅ XML saved to: {output_xml}")
    except etree.XMLSyntaxError as e:
        print("❌ XML Parsing Error:", e)

def process_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            csv_path = os.path.join(folder_path, filename)
            base_name = os.path.splitext(filename)[0]
            output_xml = os.path.join(folder_path, f"{base_name}_final.xml")
            df_entities = pd.read_csv(csv_path)
            df2xml(df_entities, output_xml)

def main():
    parser = argparse.ArgumentParser(description="Convert all CSV files in a folder to XML format.")
    parser.add_argument("folder_path", type=str, help="Path to the folder containing CSV files.")
    args = parser.parse_args()
    process_folder(args.folder_path)

if __name__ == "__main__":
    main()
