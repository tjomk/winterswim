# Icons Directory

This directory should contain the following icon files for SEO and PWA optimization:

## Required Icons

### 1. favicon.ico (32x32)
- **File:** `favicon.ico`
- **Size:** 32x32 pixels
- **Format:** ICO
- **Location:** Move to `/static/` directory (root of static files)
- **Purpose:** Browser tab icon

### 2. Apple Touch Icon (180x180)
- **File:** `apple-touch-icon.png`
- **Size:** 180x180 pixels
- **Format:** PNG
- **Location:** `/static/icons/`
- **Purpose:** iOS home screen icon

### 3. Android Icons

#### Small Icon (192x192)
- **File:** `icon-192.png`
- **Size:** 192x192 pixels
- **Format:** PNG
- **Location:** `/static/icons/`
- **Purpose:** Android home screen icon (small)

#### Large Icon (512x512)
- **File:** `icon-512.png`
- **Size:** 512x512 pixels
- **Format:** PNG
- **Location:** `/static/icons/`
- **Purpose:** Android splash screen and home screen icon (large)

## Icon Design Guidelines

- Use the snowflake ❄️ emoji or winter swimming theme
- Use blue color scheme (theme color: #0066cc)
- Ensure icons are recognizable at small sizes
- Use transparent background for PNG files
- For maskable icons (Android), ensure important content is within safe zone (80% of image)

## Tools for Creating Icons

- **Favicon Generator:** https://realfavicongenerator.net/
- **PWA Icon Generator:** https://www.pwabuilder.com/imageGenerator
- **Manual Creation:** Use any image editor (Figma, Photoshop, GIMP, etc.)

## Current Status

⚠️ **Action Required:** Icon files need to be created and placed in this directory.

The manifest.json file has been created and is referencing these icon paths. Once you create the icons, the PWA functionality will be fully enabled.
