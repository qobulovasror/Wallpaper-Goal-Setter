#!/usr/bin/env python

from root import tk, SetWallaper


def main():
    # try:
    #     root = tk.Tk()
    #     app = SetWallaper(root)
    #     root.mainloop()

    # except:
    #     print("Something went wrong")
    root = tk.Tk()
    app = SetWallaper(root)
    root.mainloop()


if __name__ == "__main__":
    main()
