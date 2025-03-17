import pygame
import pandas as pd
import tkinter as tk
from tkinter import filedialog, simpledialog
from pyproj import Transformer, CRS
import sys
import datetime
import math

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
FPS = 60
OCEAN_COLOR = (20, 40, 100)

# Initialize Tkinter
root = tk.Tk()
root.withdraw()

def detect_columns(df):
    options = [("long", "lat"), ("longitude", "latitude"), ("x", "y")]
    for x, y in options:
        if x in df.columns and y in df.columns:
            return x, y
    return None, None

def detect_time_column(df):
    for col in df.columns:
        try:
            pd.to_datetime(df[col])
            return col
        except:
            continue
    return None

def prompt_manual_column_selection(df):
    col_names = df.columns.tolist()
    x_col = simpledialog.askstring("Manual Column Selection", f"Enter X (Longitude) column:\n{col_names}")
    y_col = simpledialog.askstring("Manual Column Selection", f"Enter Y (Latitude) column:\n{col_names}")
    t_col = simpledialog.askstring("Manual Column Selection", f"Enter Time column:\n{col_names}")
    return x_col, y_col, t_col

def load_and_process_csv():
    file_path = filedialog.askopenfilename(title="Select CSV", filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        sys.exit("No file selected.")

    df = pd.read_csv(file_path)
    x_col, y_col = detect_columns(df)
    t_col = detect_time_column(df)

    override = simpledialog.askstring("Override", "Manual override column detection? (yes/no)").lower()
    if override == "yes":
        x_col, y_col, t_col = prompt_manual_column_selection(df)

    df = df.dropna(subset=[x_col, y_col, t_col])
    df[t_col] = pd.to_datetime(df[t_col])

    projection_input = simpledialog.askstring("Projection", "Enter projection (e.g., EPSG:4326)", initialvalue="EPSG:4326")
    transformer = Transformer.from_crs(CRS(projection_input), CRS("EPSG:4326"), always_xy=True)

    df['lon'], df['lat'] = zip(*df.apply(lambda row: transformer.transform(row[x_col], row[y_col]), axis=1))
    df['timestamp'] = df[t_col]

    id_col = None
    for col in df.columns:
        if "id" in col.lower():
            id_col = col
            break

    return df[['lon', 'lat', 'timestamp']] if not id_col else df[['lon', 'lat', 'timestamp', id_col]]

def latlon_to_screen(lat, lon):
    x = (lon + 180) * (WINDOW_WIDTH / 360)
    y = (90 - lat) * (WINDOW_HEIGHT / 180)
    return int(x), int(y)

def interpolate_points(p1, p2, t1, t2, steps=10):
    result = []
    for i in range(steps):
        f = i / steps
        lon = p1[0] + f * (p2[0] - p1[0])
        lat = p1[1] + f * (p2[1] - p1[1])
        timestamp = t1 + (t2 - t1) * f
        result.append((lon, lat, timestamp))
    return result

def calculate_steps(p1, p2, t1, t2):
    dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
    time_diff = (t2 - t1).total_seconds()
    return max(5, min(50, int(dist * time_diff / 1000)))

def draw_background(screen):
    screen.fill(OCEAN_COLOR)
    for lon in range(-180, 181, 30):
        x, _ = latlon_to_screen(0, lon)
        pygame.draw.line(screen, (30, 60, 130), (x, 0), (x, WINDOW_HEIGHT), 1)
    for lat in range(-90, 91, 30):
        _, y = latlon_to_screen(lat, 0)
        pygame.draw.line(screen, (30, 60, 130), (0, y), (WINDOW_WIDTH, y), 1)

def main():
    data = load_and_process_csv()
    path = []
    for i in range(len(data) - 1):
        p1 = (data.loc[i, 'lon'], data.loc[i, 'lat'])
        p2 = (data.loc[i+1, 'lon'], data.loc[i+1, 'lat'])
        t1 = data.loc[i, 'timestamp']
        t2 = data.loc[i+1, 'timestamp']
        steps = calculate_steps(p1, p2, t1, t2)
        path.extend(interpolate_points(p1, p2, t1, t2, steps))

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Geospatial Point Animation")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    running = True
    dt = 0
    frame = 0

    while running:
        # --- Handle Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Draw ---
        draw_background(screen)

        if frame < len(path):
            lon, lat, timestamp = path[frame]
            x, y = latlon_to_screen(lat, lon)
            pygame.draw.circle(screen, (255, 0, 0), (x, y), 6)

            text = f"Lon: {lon:.4f}, Lat: {lat:.4f}, Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            label = font.render(text, True, (255, 255, 255))
            screen.blit(label, (10, 10))

            frame += 1
        else:
            frame = 0  # Loop or stop

        pygame.display.flip()
        dt = clock.tick(FPS) / 1000

    pygame.quit()

if __name__ == "__main__":
    main()