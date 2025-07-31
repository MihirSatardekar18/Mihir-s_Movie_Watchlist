import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import json, os

FILE = "movies.json"

# Load data
def load_movies():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return json.load(f)
    return []

# Save data
def save_movies():
    with open(FILE, "w") as f:
        json.dump(movies, f)

# Add movie
def add_movie():
    title = title_var.get().strip()
    note = note_var.get().strip()
    poster = poster_var.get().strip()

    if title and poster:
        movies.append({"title": title, "note": note, "poster": poster, "watched": False})
        save_movies()
        update_list()
        title_var.set("")
        note_var.set("")
        poster_var.set("")
    else:
        messagebox.showwarning("Input", "Enter movie title and poster path.")

# Delete movie
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

# Show poster
def show_poster(event):
    selected = tree.selection()
    if selected:
        index = int(selected[0])
        poster_path = movies[index].get("poster", "")
        if os.path.exists(poster_path):
            img = Image.open(poster_path)
            img = img.resize((200, 300))
            img = ImageTk.PhotoImage(img)
            poster_label.config(image=img)
            poster_label.image = img
        else:
            poster_label.config(image="", text="Poster not found.")

# Update treeview
def update_list():
    tree.delete(*tree.get_children())
    for i, m in enumerate(movies):
        status = "✅" if m["watched"] else "❌"
        tree.insert("", "end", iid=i, values=(m["title"], m["note"], status))

# GUI Setup
root = tk.Tk()
root.title("🎬 Mihir's Movie Watchlist")
root.geometry("700x550")

title_var = tk.StringVar()
note_var = tk.StringVar()
poster_var = tk.StringVar()
movies = load_movies()

tk.Label(root, text="Movie Title:").pack()
tk.Entry(root, textvariable=title_var, width=50).pack()

tk.Label(root, text="Note (Optional):").pack()
tk.Entry(root, textvariable=note_var, width=50).pack()

tk.Label(root, text="Poster Path (.jpg/.png):").pack()
tk.Entry(root, textvariable=poster_var, width=50).pack(pady=5)

tk.Button(root, text="Add Movie", command=add_movie).pack(pady=5)

tree = ttk.Treeview(root, columns=("Title", "Note", "Watched"), show="headings")
tree.heading("Title", text="Title")
tree.heading("Note", text="Note")
tree.heading("Watched", text="Watched")
tree.bind("<<TreeviewSelect>>", show_poster)
tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

tk.Button(root, text="Mark as Watched", command=mark_watched).pack(pady=2)
tk.Button(root, text="Delete Movie", command=delete_movie).pack(pady=2)

poster_label = tk.Label(root)
poster_label.pack(pady=10)

update_list()
root.mainloop()
