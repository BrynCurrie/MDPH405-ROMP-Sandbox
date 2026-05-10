import matplotlib

matplotlib.use('TkAgg')  # Must be before importing pyplot

import os
import numpy as np
import pydicom
from pydicom.uid import ImplicitVRLittleEndian
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.patches import Polygon
import tkinter as tk
from tkinter import filedialog
from collections import Counter
from scipy.ndimage import zoom  # For dose resampling


def load_image_series(folder):
    files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(('.dcm', '.dicom'))]
    if not files:
        raise ValueError("No DICOM files found in the selected folder.")

    datasets = []
    shapes = set()

    for f in files:
        ds = pydicom.dcmread(f, force=True)
        if not hasattr(ds.file_meta, 'TransferSyntaxUID') or ds.file_meta.TransferSyntaxUID is None:
            ds.file_meta.TransferSyntaxUID = ImplicitVRLittleEndian
        if 'PixelData' in ds and 'ImagePositionPatient' in ds:
            try:
                pixel_arr = ds.pixel_array
                current_shape = pixel_arr.shape
                shapes.add(current_shape)
                datasets.append(ds)
                print(f"Loaded: {os.path.basename(f)} - Shape: {current_shape}")
            except Exception as e:
                print(f"Skipped (decode error): {os.path.basename(f)} - {e}")

    if not datasets:
        raise ValueError("No valid image slices found.")

    print(f"\nUnique shapes found: {shapes}")

    shape_counts = Counter(d.pixel_array.shape for d in datasets)
    most_common_shape = shape_counts.most_common(1)[0][0]
    print(f"Most common shape: {most_common_shape} (count: {shape_counts[most_common_shape]})")

    filtered_datasets = [ds for ds in datasets if ds.pixel_array.shape == most_common_shape]

    if len(filtered_datasets) < len(datasets):
        print(f"Filtered out {len(datasets) - len(filtered_datasets)} slices with mismatched shapes.")

    if not filtered_datasets:
        raise ValueError("No slices with consistent shape after filtering.")

    filtered_datasets.sort(key=lambda ds: float(ds.ImagePositionPatient[2]))

    pixels = np.stack([ds.pixel_array for ds in filtered_datasets])
    positions = [float(ds.ImagePositionPatient[2]) for ds in filtered_datasets]
    spacing = filtered_datasets[0].PixelSpacing

    print(f"Final volume shape: {pixels.shape} (slices x rows x cols)")

    return pixels, positions, spacing, filtered_datasets[0]


def world_to_pixel(point_world, ref_ds):
    ipp = np.array(ref_ds.ImagePositionPatient)
    iop = np.array(ref_ds.ImageOrientationPatient).reshape(2, 3)
    ps = np.array(ref_ds.PixelSpacing)
    row_dir = iop[0]
    col_dir = iop[1]
    offset = point_world - ipp
    col = np.dot(offset, col_dir) / ps[0]
    row = np.dot(offset, row_dir) / ps[1]
    return row, col


def get_contours_per_slice(rtstruct_ds, ref_ds):
    contours_by_z = {}
    for roi_seq in rtstruct_ds.ROIContourSequence:
        color = tuple([c / 255 for c in roi_seq.ROIDisplayColor]) if 'ROIDisplayColor' in roi_seq else (1, 0, 0)
        for contour_seq in roi_seq.ContourSequence:
            if contour_seq.ContourGeometricType != 'CLOSED_PLANAR':
                continue
            points = np.array(contour_seq.ContourData).reshape(-1, 3)
            z = points[0, 2]
            pixel_points = [world_to_pixel(p, ref_ds) for p in points]
            if z not in contours_by_z:
                contours_by_z[z] = []
            contours_by_z[z].append((pixel_points, color))
    return contours_by_z


def load_dose(rt_dose_file, ref_ds, pixels_shape, z_positions):
    dose_ds = pydicom.dcmread(rt_dose_file, force=True)
    if not hasattr(dose_ds.file_meta, 'TransferSyntaxUID') or dose_ds.file_meta.TransferSyntaxUID is None:
        dose_ds.file_meta.TransferSyntaxUID = ImplicitVRLittleEndian

    dose_grid = dose_ds.pixel_array * float(dose_ds.DoseGridScaling)

    ipp = np.array(dose_ds.ImagePositionPatient)
    z_dose = ipp[2] + np.array(dose_ds.GridFrameOffsetVector)

    target_rows, target_cols = pixels_shape[1], pixels_shape[2]
    dose_rows, dose_cols = dose_ds.Rows, dose_ds.Columns

    zoom_factors = (target_rows / dose_rows, target_cols / dose_cols)

    dose_volume = np.zeros(pixels_shape, dtype=np.float32)

    for i, z_ct in enumerate(z_positions):
        idx = np.argmin(np.abs(z_dose - z_ct))
        if abs(z_dose[idx] - z_ct) < 5.0:  # Within 5 mm
            dose_slice = dose_grid[idx]
            resized_slice = zoom(dose_slice, zoom_factors, order=0, mode='nearest')
            dose_volume[i] = resized_slice

    return dose_volume


# =================== MAIN CODE ===================

root = tk.Tk()
root.withdraw()

# Select CT folder
image_folder = filedialog.askdirectory(title="Select folder containing CT/MR DICOM slices")
if not image_folder:
    print("No folder selected. Exiting.")
    exit()

# Select RTSTRUCT
rtstruct_file = filedialog.askopenfilename(title="Select RTSTRUCT DICOM file", filetypes=[("DICOM files", "*.dcm")])
if not rtstruct_file:
    print("No RTSTRUCT file selected. Exiting.")
    exit()

print("Loading CT images...")
pixels, z_positions, spacing, ref_ds = load_image_series(image_folder)

print("Loading structures...")
rt_ds = pydicom.dcmread(rtstruct_file, force=True)
if not hasattr(rt_ds.file_meta, 'TransferSyntaxUID') or rt_ds.file_meta.TransferSyntaxUID is None:
    rt_ds.file_meta.TransferSyntaxUID = ImplicitVRLittleEndian
contours_by_z = get_contours_per_slice(rt_ds, ref_ds)

# Optional dose
dose_file = filedialog.askopenfilename(title="Select RTDose DICOM file (optional - cancel for no dose)",
                                       filetypes=[("DICOM files", "*.dcm")])
dose_volume = None
if dose_file:
    print("Loading dose grid...")
    dose_volume = load_dose(dose_file, ref_ds, pixels.shape, z_positions)
else:
    print("No dose file selected – continuing without dose overlay.")

root.destroy()

# =================== PLOTTING ===================

fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.25)

# CT image
img = ax.imshow(pixels[0], cmap='gray', interpolation='none')

# Dose overlay
if dose_volume is not None:
    dose_overlay = ax.imshow(dose_volume[0], cmap='jet', alpha=0.4, interpolation='none',
                             vmin=0, vmax=dose_volume.max() * 0.8)
    fig.colorbar(dose_overlay, ax=ax, label='Dose (Gy)')
else:
    dose_overlay = ax.imshow(np.zeros_like(pixels[0]), cmap='jet', alpha=0.0, interpolation='none')

ax.set_aspect('equal')
polygons = []

# Sliders
ax_slice = plt.axes([0.15, 0.15, 0.65, 0.03])
slider_slice = Slider(ax_slice, 'Slice', 0, len(pixels) - 1, valinit=0, valstep=1)

ax_alpha = plt.axes([0.15, 0.08, 0.65, 0.03])
slider_alpha = Slider(ax_alpha, 'Dose Alpha', 0.0, 1.0, valinit=0.4 if dose_volume is not None else 0.0)


def update(val):
    slice_idx = int(slider_slice.val)
    alpha = slider_alpha.val

    img.set_data(pixels[slice_idx])

    if dose_volume is not None:
        dose_overlay.set_data(dose_volume[slice_idx])
        dose_overlay.set_alpha(alpha)

    # Clear and redraw contours
    for p in polygons:
        p.remove()
    polygons.clear()

    z = z_positions[slice_idx]
    for pts, color in contours_by_z.get(z, []):
        poly = Polygon(np.array(pts), fill=False, edgecolor=color, linewidth=2)
        ax.add_patch(poly)
        polygons.append(poly)

    fig.canvas.draw_idle()


slider_slice.on_changed(update)
slider_alpha.on_changed(update)
update(0)  # Initial draw

plt.show()