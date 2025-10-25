import tkinter as tk
from frontend.gui import FinanceGUI

def main():
    root = tk.Tk()
    app = FinanceGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()