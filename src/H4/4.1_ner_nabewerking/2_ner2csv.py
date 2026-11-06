import os
import xml.etree.ElementTree as ET
import pandas as pd

def extract_characters(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    char_data = []

    for page in root.findall("page"):
        page_number = page.get("number")

        for incident in page.findall("incident"):
            incident_number = incident.get("number")

            for text_element in incident:
                if text_element.tag in ["p", "marg"]:
                    paragraph_number = text_element.get("number")
                    local_char_index = 0

                    text = ET.tostring(text_element, encoding="unicode", method="text")
                    
                    for char in text:
                        if char != "\n":
                            char_data.append({
                                "page": page_number,
                                "incident": incident_number,
                                "paragraph_type": text_element.tag,
                                "structural_element_number": paragraph_number,
                                "character": char,
                                "local_char_index": local_char_index
                            })
                            local_char_index += 1

    return pd.DataFrame(char_data)

def extract_entities(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    entities = []

    for page in root.findall("page"):
        page_number = page.get("number")

        for incident in page.findall("incident"):
            incident_number = incident.get("number")

            for text_element in incident:
                if text_element.tag in ["p", "marg"]:
                    paragraph_number = text_element.get("number")
                    text_without_tags = "".join(text_element.itertext())
                    
                    for elem in text_element.iter():
                        entity_text = "".join(elem.itertext()).strip()
                        entity_type = elem.tag

                        if elem != text_element and entity_text:
                            start_index = text_without_tags.find(entity_text)
                            end_index = start_index + len(entity_text) - 1

                            if start_index != -1:
                                entities.append({
                                    "page": page_number,
                                    "incident": incident_number,
                                    "paragraph_type": text_element.tag,
                                    "structural_element_number": paragraph_number,
                                    "start_index": start_index,
                                    "end_index": end_index,
                                    "entity_type": entity_type
                                })

    return pd.DataFrame(entities)

def process_xml_folder(folder_path, output_folder):
    # Find all XML files in the folder
    xml_files = [f for f in os.listdir(folder_path) if f.endswith('.xml')]

    # Create a dictionary of base names without suffix
    file_pairs = {}
    for xml_file in xml_files:
        if xml_file.endswith('_fine.xml'):
            base_name = xml_file.replace('_fine.xml', '')
            file_pairs.setdefault(base_name, {})['fine'] = xml_file
        elif xml_file.endswith('_coarse.xml'):
            base_name = xml_file.replace('_coarse.xml', '')
            file_pairs.setdefault(base_name, {})['coarse'] = xml_file

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    for base_name, files in file_pairs.items():
        if 'fine' in files and 'coarse' in files:  # Process only if both files exist
            fine_xml_path = os.path.join(folder_path, files['fine'])
            coarse_xml_path = os.path.join(folder_path, files['coarse'])

            print(f"Processing: {files['fine']} and {files['coarse']}")

            df_entities = extract_characters(fine_xml_path)
            df_fine_entities = extract_entities(fine_xml_path)
            df_coarse_entities = extract_entities(coarse_xml_path)

            for _, row in df_fine_entities.iterrows():
                mask = (
                    (df_entities["page"] == row["page"]) &
                    (df_entities["incident"] == row["incident"]) &
                    (df_entities["structural_element_number"] == row["structural_element_number"]) &
                    (df_entities["local_char_index"] == row["start_index"])
                )
                df_entities.loc[mask, "fine_entity"] = f"B-{row['entity_type']}"

                mask = (
                    (df_entities["page"] == row["page"]) &
                    (df_entities["incident"] == row["incident"]) &
                    (df_entities["structural_element_number"] == row["structural_element_number"]) &
                    (df_entities["local_char_index"] == row["end_index"])
                )
                df_entities.loc[mask, "fine_entity"] = f"F-{row['entity_type']}"

            for _, row in df_coarse_entities.iterrows():
                mask = (
                    (df_entities["page"] == row["page"]) &
                    (df_entities["incident"] == row["incident"]) &
                    (df_entities["structural_element_number"] == row["structural_element_number"]) &
                    (df_entities["local_char_index"] == row["start_index"])
                )
                df_entities.loc[mask, "coarse_entity"] = f"B-{row['entity_type']}"

                mask = (
                    (df_entities["page"] == row["page"]) &
                    (df_entities["incident"] == row["incident"]) &
                    (df_entities["structural_element_number"] == row["structural_element_number"]) &
                    (df_entities["local_char_index"] == row["end_index"])
                )
                df_entities.loc[mask, "coarse_entity"] = f"F-{row['entity_type']}"

            # Save to CSV
            output_csv_path = os.path.join(output_folder, f"{base_name}.csv")
            df_entities.to_csv(output_csv_path, index=False)
            print(f"Saved: {output_csv_path}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process XML files in a folder.")
    parser.add_argument("folder_path", help="Path to the folder containing XML files.")
    parser.add_argument("output_folder", help="Path to the folder where CSV files will be saved.")

    args = parser.parse_args()
    
    process_xml_folder(args.folder_path, args.output_folder)
