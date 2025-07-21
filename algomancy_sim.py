import os
import random
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# Create path variables.
ELEMENTS = ["earth", "fire", "metal", "water", "wood"]
MULTI_DIR_NAME = "multi"
BASE_PATH = os.path.expanduser("C:/Users/noaha/OneDrive/Desktop/Algomancy")

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

def create_gui(cards_by_element):
    root = tk.Tk()
    root.title("Algomancy Pack Simulator")
    s = ttk.Style()
    s.configure('new.TFrame', background='#D3D3D3')
    s.configure('Card.TLabel', background='#D3D3D3')

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.configure(bg = "#a8a8a8")
    card_width, card_height = 160, 240
    image_refs = []

    def regenerate_pack():
        for widget in scroll_frame.winfo_children():
            widget.destroy()
        selected_elements = random.sample(ELEMENTS, 3)
        full_pool = get_card_pool(selected_elements)
        new_pack = random.sample(full_pool, 16)
        new_cards_by_element = {} #Group by element to sort
        for element, card in sorted(new_pack, key=lambda x: x[0]):
            new_cards_by_element.setdefault(element, []).append(card)
        display_cards(new_cards_by_element)

    # Layout Container
    root.grid_rowconfigure(0, weight = 1)
    root.grid_columnconfigure(0, weight = 1)

    main_frame = ttk.Frame(root, style='new.TFrame')
    main_frame.grid(row = 0, column = 0, sticky = "nsew")

    main_frame.grid_rowconfigure(0, weight = 1)
    main_frame.grid_columnconfigure(0, weight = 1)

    # Canvas
    canvas = tk.Canvas(main_frame, width = screen_width, height = screen_height - 80, bg="#D3D3D3")
    scroll_frame = ttk.Frame(canvas, style='new.TFrame')
    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.grid(row=0, column=0, sticky="nsew")

    # Button Frame
    button_frame = ttk.Frame(root, style='new.TFrame')
    button_frame.grid(row=1, column=0, sticky="e", pady=10, padx=20)
    ttk.Button(button_frame, text="Generate New Pack", command=regenerate_pack).pack(anchor="e")

    def display_cards(cards_by_element):
        multi_cards = {key: value for key, value in cards_by_element.items() if "-" in key}
        regular_cards = {key: value for key, value in cards_by_element.items() if "-" not in key}

        # Place multi-element cards on left
        multi_frame = ttk.Frame(scroll_frame, style='new.TFrame')
        multi_frame.grid(row=0, column=0, sticky="nw", padx=(10, 50), pady=10)

        multi_flat = []
        for element, cards in multi_cards.items():
            for card in cards:
                multi_flat.append((element, card))

        for idx, (element, card) in enumerate(multi_flat):
            col = idx // 3
            row = idx % 3
            folder_path = os.path.join(BASE_PATH, MULTI_DIR_NAME, element)
            image_path = os.path.join(folder_path, card)
            try:
                img = Image.open(image_path).resize((card_width, card_height), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                image_refs.append(photo)
                label = ttk.Label(multi_frame, image=photo, style="Card.TLabel")
                label.grid(row=row, column=col, padx=5, pady=10)

            except Exception as e:
                print(f"Error loading {image_path}: {e}")

        # Regular element cards on the right
        regular_frame = ttk.Frame(scroll_frame, style='new.TFrame')
        regular_frame.grid(row=0, column=1, sticky="nw", padx=10, pady=10)

        sorted_regular = sorted(regular_cards.items(), key=lambda x: len(x[1]), reverse=True)

        for row_idx, (element, cards) in enumerate(sorted_regular):
            row_frame = ttk.Frame(regular_frame, style='new.TFrame')
            row_frame.pack(anchor="w", pady=10)
            for card in cards:
                folder_path = os.path.join(BASE_PATH, element)
                image_path = os.path.join(folder_path, card)
                try:
                    img = Image.open(image_path).resize((card_width, card_height), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    image_refs.append(photo)
                    label = ttk.Label(row_frame, image=photo, style="Card.TLabel")
                    label.pack(side="left", padx=5)

                except Exception as e:
                    print(f"Error loading {image_path}: {e}")

    display_cards(cards_by_element)
    root.mainloop()


def main():
    selected_elements = random.sample(ELEMENTS, 3)
    full_pool = get_card_pool(selected_elements)
    pack_cards = random.sample(full_pool, 16)

    # Sort cards by element
    cards_by_element = {}
    for element, card in sorted(pack_cards, key=lambda x: x[0]):
        cards_by_element.setdefault(element, []).append(card)

    print(f"Selected Elements: {', '.join(selected_elements)}")
    create_gui(cards_by_element)

if __name__ == "__main__":
    main()