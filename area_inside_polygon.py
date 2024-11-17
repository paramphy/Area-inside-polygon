import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import json
import os
import numpy as np
import scipy.io as sc
import imutils


def convert_mat_img(filepath):

    img = sc.loadmat(filepath)["pfields"]
    ind = np.where(img > 0)
    image = np.zeros((np.size(img, 0), np.size(img, 1), 3))
    image[ind[0], ind[1], 0] = 67
    image[ind[0], ind[1], 1] = 211
    image[ind[0], ind[1], 2] = 255
    filename = filepath.strip(".mat") + "_savedImage.png"
    cv2.imwrite(filename, image)
    return filename


polygon_points = []


# Main GUI application class
class PolygonMaskingApp:
    def __init__(self, root):
        """Initializes the application with root Tkinter window."""
        self.root = root
        self.root.title("Polygon Masking Tool")

        # Buttons for functionalit
        open_button = tk.Button(
            root,
            text="Open Image",
            command=self.open_image,
            font=("Helvetica", 10, "bold"),
        )
        open_button.grid(column=0, row=1, columnspan=1, pady=5)

        open_button = tk.Button(
            root,
            text="Open Matrix file",
            command=self.open_mat_files,
            font=("Helvetica", 10, "bold"),
        )
        open_button.grid(column=0, row=2, columnspan=1, pady=5)

        save_button = tk.Button(
            root,
            text="Save Polygon Data",
            command=self.save_polygon,
            font=("Helvetica", 10, "bold"),
        )
        save_button.grid(column=0, row=3, columnspan=1, pady=5)

        reset_button = tk.Button(
            root,
            text="Reset Polygon",
            command=self.reset_polygon,
            font=("Helvetica", 10, "bold"),
        )
        reset_button.grid(column=0, row=4, columnspan=1, pady=5)

        # Label to display area
        self.area_label = tk.Label(
            root, text="Polygon Area: 0 pixels", font=("Helvetica", 16, "bold")
        )
        self.area_label.grid(column=1, row=1, rowspan=3, pady=5)

        # Label to display area
        self.total_area_label = tk.Label(
            root, text=f"Total Area: 0 pixels", font=("Helvetica", 16, "bold")
        )
        self.total_area_label.grid(column=1, row=2, rowspan=3, pady=5)

        # Label to display area
        self.fraction_area_label = tk.Label(
            root, text="Polygon Area: 0 pixels", font=("Helvetica", 16, "bold")
        )
        self.fraction_area_label.grid(column=1, row=3, rowspan=3, pady=5)

        # Label to display area
        self.instruction_label = tk.Label(
            root,
            text="LEFT click on the image to draw points. \nRIGHT click to close the polygon.",
            font=("Helvetica", 11, "italic"),
        )
        self.instruction_label.grid(column=0, row=5, columnspan=2, pady=5)

        # Image and canvas variables
        self.image_path = None
        self.canvas_image = None
        self.frame = None

    def open_image(self):
        """Opens an image file and displays it on the canvas."""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=(("Image files", "*.jpg *.png *.jpeg"), ("All files", "*.*")),
        )
        if file_path:
            self.image_path = file_path
            self.polygon_filename = file_path.strip(".png") + "_polygon_data_points.csv"
            self.load_image()
            self.display_image()

    def open_mat_files(self):
        """Opens an mat file as an image and displays it on the canvas."""
        file_path = filedialog.askopenfilename(
            title="Select *.mat file",
            filetypes=(("Matrix Files", "*.mat"), ("All files", "*.*")),
        )
        if file_path:
            self.image_path = convert_mat_img(file_path)
            self.polygon_filename = file_path.strip(".png") + "_polygon_data_points.csv"
            self.load_image()
            self.display_image()

    def load_image(self):
        """Loads the image file for display and drawing."""
        self.frame = cv2.imread(self.image_path)
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        self.frame = imutils.resize(self.frame, width=640)
        # Initialize Canvas
        self.canvas = tk.Canvas(
            root,
            width=np.shape(self.frame)[1],
            height=np.shape(self.frame)[0],
            bg="gray",
        )
        self.canvas.grid(column=0, row=0, columnspan=2, pady=5)
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.add_polygon_point)
        self.canvas.bind("<Button-3>", self.close_polygon)

    def display_image(self):
        """Displays the loaded image on the canvas."""
        img = Image.fromarray(self.frame)
        # print(img.size)
        # self.canvas = tk.Canvas(root, width=img.size[0], height=img.size[1], bg="gray")
        self.canvas_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas_image)
        self.calculate_total_area()

    def add_polygon_point(self, event):
        """Adds a point to the polygon based on canvas click coordinates."""
        x, y = event.x, event.y
        polygon_points.append((x, y))
        self.draw_polygon()

    def close_polygon(self, event=None):
        """Closes the polygon by connecting the last point to the first."""
        if len(polygon_points) > 2:
            polygon_points.append(polygon_points[0])
            self.draw_polygon()
            self.calculate_area()
            self.calculate_fractional_area()

    def reset_polygon(self):
        """Resets the polygon points for a new drawing."""
        global polygon_points
        polygon_points = []
        self.canvas.delete("all")
        self.display_image()
        self.area_label.config(text="Polygon Area: 0 pixels")
        self.fraction_area_label.config(text="Fractional Area: 0 %")

    def draw_polygon(self):
        """Draws the polygon on the canvas based on current points."""
        self.canvas.delete("polygon_lines")  # Clear previous lines
        if len(polygon_points) > 1:
            # Draw lines connecting the points
            for i in range(len(polygon_points) - 1):
                self.canvas.create_line(
                    polygon_points[i][0],
                    polygon_points[i][1],
                    polygon_points[i + 1][0],
                    polygon_points[i + 1][1],
                    fill="green",
                    width=2,
                    tags="polygon_lines",
                )

    def calculate_area(self):
        """Calculates and displays the area of the polygon in pixels."""
        if len(polygon_points) < 3:
            self.area_label.config(text="Polygon Area: 0 pixels")
            return

        # Apply the Shoelace formula
        self.area = 0
        for i in range(len(polygon_points) - 1):
            x1, y1 = polygon_points[i]
            x2, y2 = polygon_points[i + 1]
            self.area += x1 * y2 - y1 * x2
        self.area = abs(self.area) / 2
        self.area_label.config(text=f"Polygon Area: {int(self.area)} pixels")

    def calculate_total_area(self):
        if np.shape(self.frame):
            self.total_area = np.shape(self.frame)[0] * np.shape(self.frame)[1]

            self.total_area_label.config(
                text=f" Total Area: {int(self.total_area)} pixels"
            )

    def calculate_fractional_area(self):

        self.fraction_area_under_polygon = round(self.area / self.total_area, 3) * 100
        self.fraction_area_label.config(
            text=f"Fractional Area: {int(self.fraction_area_under_polygon)} %"
        )

    def save_polygon(self):
        """Saves the polygon points to a JSON file."""
        if not polygon_points:
            messagebox.showerror("Error", "No polygon points to save")
            return

        # Save polygon points to CSV
        np.savetxt(self.polygon_filename, polygon_points)

        with open(self.polygon_filename, "a") as f:
            f.write(f"\n\n# Area under the polygon (in pixcels) = {self.area}")
            f.write(f"\n\n# Total area (in pixcels) = {self.total_area}")
            f.write(
                f"\n\n# Fraction of area under the polygon (in pixcels) = {self.fraction_area_under_polygon} %"
            )

        self.masked_image_filename = (
            self.polygon_filename.strip(".csv") + "_overlay.png"
        )

        # Create a filled polygon overlay on the original image
        overlay = self.frame.copy()
        pts = np.array(
            polygon_points[:-1], np.int32
        )  # Remove the duplicated last point
        pts = pts.reshape((-1, 1, 2))

        # Fill polygon with a semi-transparent color
        mask = np.zeros_like(overlay, dtype=np.uint8)
        cv2.fillPoly(mask, [pts], color=(0, 255, 0))  # Green color

        # Blend the overlay with transparency
        alpha = 0.4  # Transparency factor
        cv2.addWeighted(mask, alpha, overlay, 1 - alpha, 0, overlay)

        # Save the overlay image
        overlay_bgr = cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR)
        cv2.imwrite(self.masked_image_filename, overlay_bgr)

        messagebox.showinfo(
            "Saved",
            f"Polygon data saved to {self.polygon_filename}\nOverlay saved to {self.masked_image_filename}",
        )

        messagebox.showinfo("Saved", f"Polygon data saved to {self.polygon_filename}")


# Initialize the Tkinter application
root = tk.Tk()
app = PolygonMaskingApp(root)
root.mainloop()
