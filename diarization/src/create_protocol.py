import json
import os
import re
import argparse

def load_protocol(file_path):
    """
    Loads the protocol from a JSON file.
    """
    with open(file_path, 'r') as file:
        return json.load(file)

def clean_protocol(protocol):
    """
    Cleans the protocol by removing multiple spaces from the text.
    """
    for segment in protocol:
        segment['text'] = re.sub(r'\s+', ' ', segment['text']).strip()
    return protocol

def filter_protocol(protocol):
    """
    Filters out segments with a duration of less than 1 second.
    """
    return [
        segment for segment in protocol
        if (segment['end'] - segment['start']) >= 1.0
    ]

def squash_consecutive_segments(protocol):
    """
    Squashes consecutive segments where the speaker is the same.
    """
    if not protocol:
        return []

    squashed_protocol = [protocol[0]]
    for segment in protocol[1:]:
        last_segment = squashed_protocol[-1]
        if segment['speaker'] == last_segment['speaker']:
            last_segment['end'] = segment['end']
            last_segment['text'] += " " + segment['text']
        else:
            squashed_protocol.append(segment)
    return squashed_protocol


def save_protocol_as_text(protocol, output_file):
    """
    Saves the protocol to a text file in a readable format.
    """
    with open(output_file, 'w') as text_file:
        for entry in protocol:
            text_file.write(f"{entry['start']:.0f};{entry['text']}\n")

def main(input_file):
    if not os.path.exists(input_file):
        print(f"File {input_file} does not exist.")
        return

    protocol = load_protocol(input_file)
    protocol = clean_protocol(protocol)
    protocol = filter_protocol(protocol)
    protocol = squash_consecutive_segments(protocol)

    base_dir = os.path.dirname(input_file)
    base_name = os.path.basename(input_file)
    name, ext = os.path.splitext(base_name)
    output_text = os.path.join(base_dir, f"prepared_{name}.txt")

    save_protocol_as_text(protocol, output_text)

    print(f"Filtered protocol saved to {output_json} and {output_text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and filter a protocol.")
    parser.add_argument("input_file", type=str, help="Path to the input protocol file")

    args = parser.parse_args()
    main(args.input_file)