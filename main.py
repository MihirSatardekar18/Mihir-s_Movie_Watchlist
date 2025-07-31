import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import json, os

FILE = "movies.json"
POSTER_FOLDER = "posters"

# Load data
def load_movies():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return json.load(f)
    return []

# Save data
def save_movies():
    with open(FILE, "w") as f:
        json.dump(movies, f, indent=2)

# Add movie
def add_movie():
    title = title_var.get().strip()
    note = note_var.get().strip()
    image_path = image_path_var.get().strip()

    if not title:
        messagebox.showwarning("Input", "Enter movie title.")
        return

    if not image_path or not os.path.exists(image_path):
        messagebox.showwarning("Image", "Enter valid image path.")
        return

    if any(m["title"].lower() == title.lower() for m in movies):
        messagebox.showwarning("Duplicate", "Movie already in the list.")
        return

    image_filename = os.path.basename(image_path)
    saved_path = os.path.join(POSTER_FOLDER, image_filename)
    os.makedirs(POSTER_FOLDER, exist_ok=True)
    with open(image_path, 'rb') as src, open(saved_path, 'wb') as dst:
        dst.write(src.read())

    movies.append({"title": title, "note": note, "watched": False, "image": saved_path})
    save_movies()
    update_list()
    title_var.set("")
    note_var.set("")
    image_path_var.set("")

# Delete selected

def delete_movie():
    selected = tree.selection()
    if selected:
        index = int(selected[0])
        movies.pop(index)
        save_movies()
        update_list()
    else:
        messagebox.showwarning("Select", "Select movie to delete.")

# Mark as watched

def mark_watched():
    selected = tree.selection()
    if selected:
        index = int(selected[0])
        movies[index]["watched"] = True
        save_movies()
        update_list()
    else:
        messagebox.showwarning("Select", "Select movie to mark as watched.")

# Update Treeview and Poster

def update_list():
    tree.delete(*tree.get_children())
    for i, m in enumerate(movies):
        status = "✅" if m["watched"] else "❌"
        tree.insert("", "end", iid=i, values=(m["title"], m["note"], status))

    # Reset poster
    poster_label.config(image="")

# Show poster when selecting a movie

def on_tree_select(event):
    selected = tree.selection()
    if selected:
        index = int(selected[0])
        img_path = movies[index].get("image")
        if img_path and os.path.exists(img_path):
            img = Image.open(img_path)
            img.thumbnail((200, 300))
            photo = ImageTk.PhotoImage(img)
            poster_label.image = photo
            poster_label.config(image=photo)

# Add recommended movie

def add_recommended(title):
    for rec in recommended_movies:
        if rec["title"] == title:
            if any(m["title"].lower() == title.lower() for m in movies):
                messagebox.showinfo("Already Added", f"{title} already in your watchlist.")
                return
            movies.append({
                "title": rec["title"],
                "note": rec["note"],
                "watched": False,
                "image": rec["image"]
            })
            save_movies()
            update_list()
            messagebox.showinfo("Added", f"{title} added to your watchlist!")
            break

# Recommended movies list
recommended_movies = [
    {"title": "The Dark Knight", "note": "Legendary Joker!", "image": "posters/dark_knight.jpg"},
    {"title": "Interstellar", "note": "Time is relative", "image": "posters/interstellar.jpg"},
    {"title": "The Matrix", "note": "Neo rocks", "image": "posters/matrix.jpg"},
    {"title": "3 Idiots", "note": "All is well!", "image": "posters/3idiots.jpg"},
    {"title": "Dangal", "note": "Women power", "image": "posters/dangal.jpg"},
]

# GUI setup
root = tk.Tk()
root.title("Mihir's Movie Watchlist")
root.geometry("800x600")

main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Left side: Add Movie + Recommended
left_frame = tk.Frame(main_frame)
left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

tk.Label(left_frame, text="Movie Title:").pack()
title_var = tk.StringVar()
tk.Entry(left_frame, textvariable=title_var, width=30).pack()

tk.Label(left_frame, text="Note (Optional):").pack()
note_var = tk.StringVar()
tk.Entry(left_frame, textvariable=note_var, width=30).pack()

tk.Label(left_frame, text="Poster Path:").pack()
image_path_var = tk.StringVar()
tk.Entry(left_frame, textvariable=image_path_var, width=30).pack()

tk.Button(left_frame, text="Add Movie", command=add_movie).pack(pady=5)
tk.Button(left_frame, text="Mark as Watched", command=mark_watched).pack(pady=2)
tk.Button(left_frame, text="Delete Movie", command=delete_movie).pack(pady=2)

# Recommended Movie Frame
rec_frame = tk.LabelFrame(left_frame, text="🎥 Recommended Movies", padx=5, pady=5)
rec_frame.pack(fill=tk.BOTH, pady=10)

for rec in recommended_movies:
    btn = tk.Button(rec_frame, text=rec["title"], width=25,
                    command=lambda t=rec["title"]: add_recommended(t))
    btn.pack(pady=1)

# Right side: Movie List and Poster
right_frame = tk.Frame(main_frame)
right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

tree = ttk.Treeview(right_frame, columns=("Title", "Note", "Watched"), show="headings")
tree.heading("Title", text="Title")
tree.heading("Note", text="Note")
tree.heading("Watched", text="Watched")
tree.pack(fill=tk.BOTH, expand=True)
tree.bind("<<TreeviewSelect>>", on_tree_select)

poster_label = tk.Label(right_frame)
poster_label.pack(pady=10)

movies = load_movies()
update_list()

root.mainloop()
