import os

# Create path variables.
ELEMENTS = ["earth", "fire", "metal", "water", "wood"]
MULTI_DIR_NAME = "multi"
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

def get_card_pool(selected_elements):
    card_pool = []

    # Add single-element cards
    for element in selected_elements:
        element_path = os.path.join(BASE_PATH, element)
        card_pool.extend([(element, card) for card in os.listdir(element_path) if os.path.isfile(os.path.join(element_path, card))])

    # Determine multi-element folders
    multi_folders = []
    for i in range(len(selected_elements)):
        for j in range(i + 1, len(selected_elements)):
            sorted_pair = sorted([selected_elements[i], selected_elements[j]])
            multi_folders.append(f"{sorted_pair[0]}-{sorted_pair[1]}")

    # Add multi-element cards
    multi_base_path = os.path.join(BASE_PATH, MULTI_DIR_NAME)
    for folder in multi_folders:
        folder_path = os.path.join(multi_base_path, folder)
        if os.path.isdir(folder_path):
            card_pool.extend([(folder, card) for card in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, card))])

    return card_pool