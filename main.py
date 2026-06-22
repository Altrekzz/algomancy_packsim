import os
import random
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from cards import get_card_pool, ELEMENTS, BASE_PATH, MULTI_DIR_NAME

def create_gui(cards_by_element):
    root = tk.Tk()
    root.title("Algomancy Pack Simulator")
    s = ttk.Style()
    s.configure('new.TFrame', background='#D3D3D3')
    s.configure('Card.TLabel', background='#D3D3D3')

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.configure(bg = "#a8a8a8")
    try:
        root.state("zoomed")
    except tk.TclError:
        root.geometry(f"{screen_width}x{screen_height}")

    GRID_ROWS, GRID_COLS = 4, 9
    CARD_ASPECT = 160/240
    PAD_X = PAD_Y = 16
    MARGIN = 20
    MAX_CARD_H = 320

    occupied = {}
    card_cell = {}
    card_src = {}
    photo_refs = {}
    picks = {}
    geom = {}
    drag_data = {"item": None, "dx": 0, "dy": 0, "orig": None}
    resize_job:dict[str, str | None] = {"id": None}

    def regenerate_pack():
        selected_elements = random.sample(ELEMENTS, 3)
        full_pool = get_card_pool(selected_elements)
        new_pack = random.sample(full_pool, 16)
        new_cards_by_element = {}
        for element, card in sorted(new_pack, key=lambda x: x[0]):
            new_cards_by_element.setdefault(element, []).append(card)
        display_cards(new_cards_by_element)

    def compute_geom():
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width <= 1:
            width = canvas.winfo_screenwidth()
        if height <= 1:
            height = canvas.winfo_screenheight()
        cell_w = max(1, (width - 2 * MARGIN) / GRID_COLS)
        cell_h = max(1, (height - 2 * MARGIN) / GRID_ROWS)
        card_h = min(cell_h - PAD_Y, (cell_w - PAD_X) / CARD_ASPECT, MAX_CARD_H)
        card_h = max(10, card_h)
        card_w = card_h * CARD_ASPECT

        geom.update(cell_w = cell_w, cell_h = cell_h, card_w = card_w, card_h = card_h,
                    off_x = (cell_w - card_w) / 2, off_y = (cell_h - card_h) / 2)
        
    def cell_to_xy(row, col):
        return(MARGIN + col * geom["cell_w"] + geom["off_x"],
               MARGIN + row * geom["cell_h"] + geom["off_y"])

    def xy_to_cell(x, y):
        col = round((x - MARGIN - geom["off_x"]) / geom["cell_w"])
        row = round((y - MARGIN - geom["off_y"]) / geom["cell_h"])
        col = max(0, min(GRID_COLS - 1, col))
        row = max(0, min(GRID_ROWS - 1, row))
        return row, col

    root.grid_rowconfigure(0, weight = 1)
    root.grid_columnconfigure(0, weight = 1)

    main_frame = ttk.Frame(root, style='new.TFrame')
    main_frame.grid(row = 0, column = 0, sticky = "nsew")

    main_frame.grid_rowconfigure(0, weight = 1)
    main_frame.grid_columnconfigure(0, weight = 1)

    canvas = tk.Canvas(main_frame, bg = "#D3D3D3", highlightthickness = 0)
    canvas.grid(row = 0, column = 0, sticky = "nsew")

    button_frame = ttk.Frame(root, style='new.TFrame')
    button_frame.grid(row=1, column=0, sticky="e", pady=10, padx=20)
    ttk.Button(button_frame, text="Generate New Pack", command=regenerate_pack).pack(anchor="e")

    def first_free_cell():
        for row in range(GRID_ROWS):
            for column in range(GRID_COLS):
                if (row, column) not in occupied:
                    return row, column
        return None
    
    def sync_border(item):
        rect = picks.get(item)
        if rect is None:
            return
        x, y = canvas.coords(item)
        canvas.coords(rect, x - 5, y - 5, x + geom["card_w"] + 5, y + geom["card_h"] + 5)

    def relayout():
        resize_job["id"] = None
        compute_geom()
        size = (max(1, round(geom["card_w"])), max(1, round(geom["card_h"])))

        for item, src in card_src.items():
            photo = ImageTk.PhotoImage(src.resize(size, Image.Resampling.LANCZOS))
            photo_refs[item] = photo
            canvas.itemconfigure(item, image = photo)
            canvas.coords(item, *cell_to_xy(*card_cell[item]))
            sync_border(item)
        
    def schedule_relayout(event = None):
        if resize_job["id"] is not None:
            root.after_cancel(resize_job["id"])
        resize_job["id"] = root.after(60, relayout)
    
    def place(src, desired):
        row, col = desired
        if not (0 <= row < GRID_ROWS and 0 <= col < GRID_COLS) or (row, col) in occupied:
            free = first_free_cell()
            if free is None:
                return
            row, col = free
        item = canvas.create_image(0, 0, anchor = "nw", tags = "card")
        occupied[(row, col)] = item
        card_cell[item] = (row, col)
        card_src[item] = src

    def on_press(event):
        current = canvas.find_withtag("current")
        if not current:
            return
        item = current[0]
        drag_data["item"] = item
        drag_data["orig"] = card_cell[item]
        ix, iy = canvas.coords(item)
        drag_data["dx"] = canvas.canvasx(event.x) - ix
        drag_data["dy"] = canvas.canvasy(event.y) - iy
        canvas.tag_raise(item)
        sync_border(item)
    
    def on_drag(event):
        item = drag_data["item"]
        if item is None:
            return
        nx = canvas.canvasx(event.x) - drag_data["dx"]
        ny = canvas.canvasy(event.y) - drag_data["dy"]
        canvas.coords(item, nx, ny)
        sync_border(item)

    def on_release(event):
        item = drag_data["item"]
        if item is None:
            return
        nx, ny = canvas.coords(item)
        orig = drag_data["orig"]
        target = xy_to_cell(nx, ny)
        if target == orig or target not in occupied:
            del occupied[orig]
            occupied[target] = item
            card_cell[item] = target
        else:
            target = orig
        canvas.coords(item, *cell_to_xy(*target))
        sync_border(item)
        drag_data["item"] = None

    def on_right_click(event):
        current = canvas.find_withtag("current")
        if not current:
            return
        item = current[0]
        if item in picks:
            canvas.delete(picks.pop(item))
        elif len(picks) < 6:
            rect = canvas.create_rectangle(0, 0, 0, 0, outline = "#E63946", width = 4, tags = "pick")
            picks[item] = rect
            sync_border(item)

    canvas.tag_bind("card", "<ButtonPress-1>", on_press)
    canvas.tag_bind("card", "<B1-Motion>", on_drag)
    canvas.tag_bind("card", "<ButtonRelease-1>", on_release)
    canvas.tag_bind("card", "<ButtonPress-3>", on_right_click)
    canvas.bind("<Configure>", schedule_relayout)
     
    def display_cards(cards_by_element):
        canvas.delete("all")
        occupied.clear()
        card_cell.clear()
        card_src.clear()
        photo_refs.clear()
        picks.clear()
        multi_cards = {key: value for key, value in cards_by_element.items() if "-" in key}
        regular_cards = {key: value for key, value in cards_by_element.items() if "-" not in key}

        multi_flat = []
        for element, cards in multi_cards.items():
            for card in cards:
                multi_flat.append((element, card))

        for idx, (element, card) in enumerate(multi_flat):
            desired = (idx % GRID_ROWS, idx // GRID_ROWS)
            image_path = os.path.join(BASE_PATH, MULTI_DIR_NAME, element, card)

            try:
                place(Image.open(image_path), desired)
            except Exception as e:
                print(f"Error loading {image_path}:{e}")

        multi_cols = -(-len(multi_flat)//GRID_ROWS)
        start_col = multi_cols +1 if multi_cols else 0
        avail_cols = max(1, GRID_COLS - start_col)
        sorted_regular = sorted(regular_cards.items(), key = lambda x: len(x[1]), reverse = True)

        next_row = 0
        for element, cards in sorted_regular:
            for col_idx, card in enumerate(cards):
                desired = (next_row + col_idx // avail_cols, start_col + col_idx % avail_cols)
                image_path = os.path.join(BASE_PATH, element, card)
                
                try:
                    place(Image.open(image_path), desired)
                except Exception as e:
                    print(f"Error loading {image_path}:{e}")

            next_row += -(-len(cards) // avail_cols)
        relayout()

    display_cards(cards_by_element)
    root.mainloop()

def main():
    selected_elements = random.sample(ELEMENTS, 3)
    full_pool = get_card_pool(selected_elements)
    pack_cards = random.sample(full_pool, 16)

    cards_by_element = {}
    for element, card in sorted(pack_cards, key=lambda x: x[0]):
        cards_by_element.setdefault(element, []).append(card)

    print(f"Selected Elements: {', '.join(selected_elements)}")
    create_gui(cards_by_element)

if __name__ == "__main__":
    main()