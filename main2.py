# main.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import json, os, threading
import imageio

# -------------- Config ----------------
USER_FILE = "users.json"
MOVIE_FILE = "movies.json"

# Dummy user data for testing
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({"admin": "admin123"}, f)

# Load movie data
if not os.path.exists(MOVIE_FILE):
    with open(MOVIE_FILE, "w") as f:
        json.dump([], f)

# -------------- App Class ----------------
class NetflixApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🎬 MihirFlix Movies Watchlist")
        self.geometry("1150x750")
        self.resizable(False, False)
        self.configure(bg="black")

        self.frames = {}
        for F in (HomePage, LoginPage, WatchlistPage):
            frame = F(self)
            self.frames[F] = frame
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        self.show_frame(HomePage)

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()

# -------------- Home Page ----------------
class HomePage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="black")
        tk.Label(self, text="MihirFlix Movies Watchlist", font=("Helvetica", 40, "bold"), fg="red", bg="black").pack(pady=100)
        tk.Label(self, text="Your Personalized Movie Watchlist App", font=("Helvetica", 18), fg="white", bg="black").pack(pady=10)
        tk.Button(self, text="Login to Continue ▶", font=("Arial", 16), command=lambda: master.show_frame(LoginPage), bg="red", fg="white", padx=20, pady=10).pack(pady=40)

# -------------- Login Page ----------------
class LoginPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#222")

        tk.Label(self, text="🔐 Login", font=("Arial", 28, "bold"), fg="white", bg="#222").pack(pady=60)

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self.create_input("Username", self.username_var)
        self.create_input("Password", self.password_var, show="*")

        tk.Button(self, text="Login", font=("Arial", 14), command=self.login, bg="red", fg="white", padx=10, pady=5).pack(pady=20)
        tk.Button(self, text="Back to Home", font=("Arial", 10), command=lambda: master.show_frame(HomePage), bg="#444", fg="white").pack()

    def create_input(self, label, var, show=None):
        frame = tk.Frame(self, bg="#222")
        tk.Label(frame, text=label, fg="white", bg="#222", anchor="w", font=("Arial", 12)).pack(anchor="w")
        tk.Entry(frame, textvariable=var, font=("Arial", 12), width=30, show=show).pack(pady=5)
        frame.pack(pady=10)

    def login(self):
        uname = self.username_var.get().strip()
        pwd = self.password_var.get().strip()
        with open(USER_FILE, "r") as f:
            users = json.load(f)
        if uname in users and users[uname] == pwd:
            self.master.show_frame(WatchlistPage)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

# -------------- Watchlist Page ----------------
class WatchlistPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#ecf0f1")

        self.movies = self.load_movies()
        self.recommendations = {
            "Inception": ["Interstellar", "Tenet", "The Prestige"],
            "Avengers": ["Iron Man", "Captain America", "Thor"],
            "3 Idiots": ["PK", "Taare Zameen Par", "Munna Bhai MBBS"]
        }

        self.video_playing = False

        # Setup variables
        self.title_var = tk.StringVar()
        self.note_var = tk.StringVar()
        self.genre_var = tk.StringVar()
        self.poster_var = tk.StringVar()
        self.video_var = tk.StringVar()
        self.genre_filter_var = tk.StringVar()

        self.build_gui()

    def load_movies(self):
        with open(MOVIE_FILE, "r") as f:
            return json.load(f)

    def save_movies(self):
        with open(MOVIE_FILE, "w") as f:
            json.dump(self.movies, f)

    def build_gui(self):
        # Left panel - Form
        form_frame = tk.Frame(self, bg="#d6eaf8", bd=2, relief="ridge")
        form_frame.place(x=20, y=20, width=350, height=340)

        tk.Label(form_frame, text="🎬 Add New Movie", font=("Arial", 14, "bold"), bg="#d6eaf8").pack(pady=10)

        self.create_form_field(form_frame, "Title:", self.title_var)
        self.create_form_field(form_frame, "Note:", self.note_var)
        self.create_form_field(form_frame, "Genre:", self.genre_var)
        self.create_form_field(form_frame, "Poster Path:", self.poster_var)
        self.create_form_field(form_frame, "Video Path:", self.video_var)

        tk.Button(form_frame, text="➕ Add Movie", command=self.add_movie, bg="#2ecc71", fg="white", font=('Arial', 11, 'bold')).pack(pady=10)

        # Genre Filter
        filter_frame = tk.LabelFrame(self, text="🔍 Filter by Genre", bg="#ecf0f1", font=("Arial", 10, "bold"))
        filter_frame.place(x=20, y=370, width=350, height=100)

        self.genre_filter_dropdown = ttk.Combobox(filter_frame, textvariable=self.genre_filter_var, width=25)
        self.genre_filter_dropdown.pack(pady=10)

        tk.Button(filter_frame, text="Filter", command=self.filter_by_genre, bg="#3498db", fg="white").pack(side="left", padx=5)
        tk.Button(filter_frame, text="Reset", command=self.reset_filter, bg="#e74c3c", fg="white").pack(side="right", padx=5)

        # Treeview
        tree_frame = tk.Frame(self)
        tree_frame.place(x=390, y=20, width=740, height=280)

        self.tree = ttk.Treeview(tree_frame, columns=("Title", "Note", "Genre", "Watched"), show="headings")
        for col in ("Title", "Note", "Genre", "Watched"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=160 if col == "Title" else 130, anchor="center")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Media
        media_frame = tk.Frame(self, bg="#ecf0f1")
        media_frame.place(x=390, y=310, width=740, height=320)

        self.poster_frame = tk.LabelFrame(media_frame, text="Poster", bg="white", font=("Arial", 10, "bold"))
        self.poster_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.video_frame = tk.LabelFrame(media_frame, text="Video Preview", bg="white", font=("Arial", 10, "bold"))
        self.video_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Action Buttons
        button_frame = tk.LabelFrame(self, text="Actions", bg="#ecf0f1", font=("Arial", 10, "bold"))
        button_frame.place(x=20, y=490, width=350, height=180)

        self.create_action_button(button_frame, "✅ Mark as Watched", self.mark_watched, "#1abc9c")
        self.create_action_button(button_frame, "🗑️ Delete Movie", self.delete_movie, "#e74c3c")
        self.create_action_button(button_frame, "🎁 Show Recommendations", self.show_recommendations, "#9b59b6")
        self.create_action_button(button_frame, "▶️ Play Video", self.play_video, "#2980b9")
        self.create_action_button(button_frame, "⏹️ Stop Video", self.stop_video, "#95a5a6")

        self.update_list()
        self.update_genre_dropdown()

    def create_form_field(self, parent, label, var):
        row = tk.Frame(parent, bg="#d6eaf8")
        tk.Label(row, text=label, width=12, anchor='e', bg="#d6eaf8").pack(side="left")
        tk.Entry(row, textvariable=var, width=25).pack(side="right", padx=5)
        row.pack(pady=4)

    def create_action_button(self, parent, text, command, color):
        tk.Button(parent, text=text, command=command, bg=color, fg="white", font=('Arial', 11, 'bold')).pack(fill="x", pady=4, padx=10)

    def update_list(self, filtered=None):
        self.tree.delete(*self.tree.get_children())
        source = filtered if filtered is not None else self.movies
        for i, m in enumerate(source):
            status = "✅" if m["watched"] else "❌"
            self.tree.insert("", "end", iid=i, values=(m["title"], m["note"], m["genre"], status))

    def update_genre_dropdown(self):
        genres = list({m["genre"] for m in self.movies if m["genre"]})
        self.genre_filter_dropdown['values'] = genres

    def add_movie(self):
        m = {
            "title": self.title_var.get().strip(),
            "note": self.note_var.get().strip(),
            "genre": self.genre_var.get().strip(),
            "poster": self.poster_var.get().strip(),
            "video": self.video_var.get().strip(),
            "watched": False
        }
        if m["title"]:
            self.movies.append(m)
            self.save_movies()
            self.update_list()
            self.update_genre_dropdown()
            for v in (self.title_var, self.note_var, self.genre_var, self.poster_var, self.video_var):
                v.set("")
        else:
            messagebox.showwarning("Input", "Movie title is required.")

    def delete_movie(self):
        selected = self.tree.selection()
        if selected:
            index = int(selected[0])
            self.movies.pop(index)
            self.save_movies()
            self.update_list()
            self.update_genre_dropdown()

    def mark_watched(self):
        selected = self.tree.selection()
        if selected:
            index = int(selected[0])
            self.movies[index]["watched"] = True
            self.save_movies()
            self.update_list()

    def show_recommendations(self):
        selected = self.tree.selection()
        if selected:
            index = int(selected[0])
            title = self.movies[index]["title"]
            recs = self.recommendations.get(title, [])
            rec_text = "\n".join(recs) if recs else "No recommendations."
            messagebox.showinfo(f"Recommendations for {title}", rec_text)

    def play_video(self):
        selected = self.tree.selection()
        if selected:
            index = int(selected[0])
            path = self.movies[index]["video"]
            if path and os.path.exists(path):
                self.video_playing = True
                threading.Thread(target=self.play_gif, args=(path,)).start()
            else:
                messagebox.showerror("Video", "Invalid video path")

    def play_gif(self, path):
        for widget in self.video_frame.winfo_children():
            widget.destroy()
        try:
            label = tk.Label(self.video_frame, bg="white")
            label.pack()
            for frame in imageio.get_reader(path):
                if not self.video_playing:
                    break
                img = Image.fromarray(frame)
                img = img.resize((460, 280))
                tk_img = ImageTk.PhotoImage(img)
                label.config(image=tk_img)
                label.image = tk_img
                label.update()
        except:
            tk.Label(self.video_frame, text="Cannot play", bg="white").pack()

    def stop_video(self):
        self.video_playing = False

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            index = int(selected[0])
            path = self.movies[index]["poster"]
            for widget in self.poster_frame.winfo_children():
                widget.destroy()
            try:
                img = Image.open(path)
                img = img.resize((200, 300))
                tk_img = ImageTk.PhotoImage(img)
                label = tk.Label(self.poster_frame, image=tk_img, bg="white")
                label.image = tk_img
                label.pack()
            except:
                tk.Label(self.poster_frame, text="Image not found", bg="white").pack()

    def filter_by_genre(self):
        genre = self.genre_filter_var.get().strip().lower()
        if genre:
            filtered = [m for m in self.movies if m["genre"].lower() == genre]
            self.update_list(filtered)

    def reset_filter(self):
        self.update_list()

# -------------- Launch ----------------
if __name__ == "__main__":
    app = NetflixApp()
    app.mainloop()
