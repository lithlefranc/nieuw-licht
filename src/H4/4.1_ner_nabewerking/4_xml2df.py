import os
import glob
import xml.etree.ElementTree as ET
import pandas as pd


def extract_persons_from_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    data = []
    person_id = 1  # Initialize Person ID counter
    incident_id = 1  # Global incident ID counter

    for page in root.findall(".//page"):
        page_number = page.get("number", "Unknown")

        for incident in page.findall(".//incident"):
            # Extract E_DATE, E_TIME, E_LOC if available
            e_date = ";".join([e.text for e in incident.findall(".//E_DATE") if e.text])
            e_time = ";".join([e.text for e in incident.findall(".//E_TIME") if e.text])
            e_loc = ";".join([e.text for e in incident.findall(".//E_LOC") if e.text])

            # Iterate over PERSON tags
            for person in incident.findall(".//PERSON"):
                person_data = {
                    "Person ID": person_id,
                    "Incident Number": incident_id,
                    "Page Number": page_number,
                    "E_DATE": e_date,
                    "E_TIME": e_time,
                    "E_LOC": e_loc
                }

                # Extract P_* tags within this PERSON, ignore tag 'PERSON' and 'P_OFFICER'
                for p_tag in person:
                    if p_tag.tag not in ["PERSON", "P_OFFICER"]:
                        person_data[p_tag.tag] = p_tag.text if p_tag.text else ""

                data.append(person_data)
                person_id += 1

            incident_id += 1

    return pd.DataFrame(data)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract PERSON data from all *_final.xml files in a folder")
    parser.add_argument('--xml_folder', required=True, help='Path to folder with *_final.xml files')
    parser.add_argument('--output_folder', required=True, help='Folder to save Excel files')
    args = parser.parse_args()

    os.makedirs(args.output_folder, exist_ok=True)

    for xml_file in glob.glob(os.path.join(args.xml_folder, '*_final.xml')):
        df = extract_persons_from_xml(xml_file)
        archive_file = os.path.basename(xml_file).replace('_final.xml', '')
        output_excel = os.path.join(args.output_folder, f'{archive_file}.xlsx')
        df.to_excel(output_excel, index=False)
        print(f"✅ Saved: {output_excel}")
