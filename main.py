#!/usr/bin/env python

from root import tk, SetWallaper

if __name__ == "__main__":
    try:

      # Set up the GUI
      root = tk.Tk()
      root.title("Wallpaper Goal Setter")

      # Text input for goals
      tk.Label(root, text="Enter your goals:").pack(pady=5)
      text_input = tk.Text(root, height=10, width=50)
      text_input.pack(pady=5)

      setWallaper = SetWallaper(root, text_input)

      # Apply changes button
      apply_button = tk.Button(
        root, text="Apply Changes", command=setWallaper.apply_changes
      )
      apply_button.pack(pady=20)

      # Run the application
      root.mainloop()
    except:
        print("Something went wrong")
