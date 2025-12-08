# Data access

This document outlines how to access the acoustic monitoring dataset collected in Wytham Woods during the 2025 field season.

## Server location
The primary acoustic data is stored on a biology domain server.

*   **Server Hostname:** `bio-lv-colefs01`
*   **Access:** Internal access only. Please inquire with the project lead for permissions.

## Directory structure
The dataset is located in the primary partition under the following path:

`data/[year]-wytham-acoustics`

### Naming convention
Top-level directories represent individual deployments. Folder names follow a grid-reference convention:

*   **Format:** `[Letter][Digit(s)]` (e.g., `A1`, `K12`)
    *   These correspond to the grid location (see [phenoscale_acoustic_loggers.csv](../metadata/phenoscale_acoustic_loggers.csv) and [logger_map.html](../metadata/logger_map.html) in this repository for explicit GPS coordinates and a visual map).
*   **Second Deployments:** Folders with a `-2` suffix (e.g., `K12-2`) indicate a second deployment at the same location.
